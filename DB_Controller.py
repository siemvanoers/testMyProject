from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_URI = 'mongodb://hrml_t02:1Mp8x8c@mongo.adainforma.tk:27017/hrml_t02?authSource=hrml_t02'
DATABASE_NAME = 'hrml_t02'
RESUMES_COLLECTION = 'resume'
VACANCIES_COLLECTION = 'vacancies'

def get_db_connection():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    print(f"Connected to MongoDB database: {DATABASE_NAME}")
    return db

def get_resume_by_id(resume_id):
    db = get_db_connection()
    resumes_collection = db[RESUMES_COLLECTION]

    if not isinstance(resume_id, ObjectId):
        resume_id = ObjectId(resume_id)

    resume = resumes_collection.find_one({"_id": resume_id})

    if resume:
        print(f"Resume found: {resume}")
        return resume
    else:
        print(f"No resume found with ID: {resume_id}")
        return None

def update_resume_by_id(resume_id, update_fields):
    db = get_db_connection()
    resumes_collection = db[RESUMES_COLLECTION]

    if not isinstance(resume_id, ObjectId):
        resume_id = ObjectId(resume_id)

    result = resumes_collection.update_one({"_id": resume_id}, {"$set": update_fields})

    if result.modified_count > 0:
        print(f"Resume with ID: {resume_id} updated successfully.")
    else:
        print(f"No resume found with ID: {resume_id} or no changes made.")

def get_vacancy_by_id(vacancy_id):
    db = get_db_connection()
    vacancies_collection = db[VACANCIES_COLLECTION]

    if not isinstance(vacancy_id, ObjectId):
        vacancy_id = ObjectId(vacancy_id)

    vacancy = vacancies_collection.find_one({"_id": vacancy_id})

    if vacancy:
        print(f"Vacancy found: {vacancy}")
        return vacancy
    else:
        print(f"No vacancy found with ID: {vacancy_id}")
        return None