import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from DB_Controller import get_resume_by_id, get_vacancy_by_id, update_resume_by_id
from bson.objectid import ObjectId
import re
import requests

def extract_skills(text):
    """
    Extracts the skills from a longtext field in the resume.
    Assumes skills are listed under a heading like "Vaardigheden" or "Skills".
    """
    print(f"Longtext content: {text}")  # Print the longtext content for debugging
    match = re.search(r'(vaardigheden|skills)\s*[\n:]*\s*([\s\S]*?)(\n\s*\n|\Z)', text, re.IGNORECASE)
    if match:
        skills_text = match.group(2).strip()
        skills_list = re.split(r'\s*[\n,•]\s*', skills_text)
        skills_list = [skill for skill in skills_list if skill]  # Remove empty strings
        return ', '.join(skills_list)
    return ""

def calculate_match_percentage(resume_skills, vacancy_skills):
    if not resume_skills or not vacancy_skills:
        return 0.0
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_skills, vacancy_skills])
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
    match_percentage = similarity_matrix[0][1] * 100
    return match_percentage


def upload_resume_and_calculate_match(user_id, vacancy_id, resume_text):
    """
    Upload the resume text and calculate match percentage with the given vacancy_id.
    """
    # Extract skills from the resume text
    resume_skills = extract_skills(resume_text)

    # Fetch the vacancy details
    response = requests.get(f"http://localhost:3000/api/vacancies/{vacancy_id}")
    if response.status_code != 200:
        print("Vacancy not found or error in fetching vacancy details.")
        return

    vacancy_data = response.json()
    vacancy_skills = vacancy_data.get("skills", "")

    # Calculate match percentage
    match_percentage = calculate_match_percentage(resume_skills, vacancy_skills)
    print(f"Calculated Match Percentage: {match_percentage}%")

    # Save match percentage to resume record in the database
    resume_data = {
        "user_id": user_id,
        "vacature_id": vacancy_id,
        "cvText": resume_text,
        "matchPercentage": match_percentage
    }

    update_response = requests.post(f"http://localhost:3000/api/upload-cv", json=resume_data)
    if update_response.status_code == 200:
        print("Resume and match percentage uploaded successfully.")
    else:
        print("Failed to upload resume and match percentage.")

def main(resume_id):
    # Fetch the resume data from the endpoint
    response = requests.get(f'https://api-android-c020.onrender.com/api/cv/{resume_id}')
    if response.status_code == 200:
        resume_data = response.json()
        if resume_data:
            resume = get_resume_by_id(ObjectId(resume_id))

            if resume:
                print("Resume document:", resume)
                vacatures_id = resume.get('vacatures_id')
                if vacatures_id:
                    vacancy = get_vacancy_by_id(vacatures_id)
                    if vacancy:
                        print("Vacancy document:", vacancy)
                        vacancy_skills = vacancy.get('skills', '')
                        print(f"Extracted Vacancy Skills: {vacancy_skills}")

                        # Extract skills from resume's longtext field
                        resume_skills = extract_skills(resume.get('cvText', ''))
                        print(f"Extracted Resume Skills: {resume_skills}")

                        # Calculate the match percentage
                        match_percentage = calculate_match_percentage(resume_skills, vacancy_skills)
                        print(f"Match Percentage: {match_percentage:.2f}%")

                        # Update the resume with the match percentage
                        update_resume_by_id(resume_id, {"matchPercentage": match_percentage})
                    else:
                        print("No connected vacancy found.")
                else:
                    print("No vacatures_id found in the resume.")
            else:
                print("No resume found with the given ID.")
        else:
            print("No resume data found in the response.")
    else:
        print(f"Failed to fetch resume data. Status code: {response.status_code}")