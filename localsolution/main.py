from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import csv
from database import SessionLocal
from models import Department, Job, Employee
import os
from datetime import datetime

app = FastAPI()

DEPARTMENTS_FILE_PATH = "C:\PROYECTOS\globant\departments.csv"
JOBS_FILE_PATH = "C:\PROYECTOS\globant\jobs.csv"
EMPLOYEES_FILE_PATH = "C:\PROYECTOS\globant\hired_employees.csv"

@app.get("/")
def read_root():
    return {"message": "Welcome to the API for DB migration!"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/")
async def upload_csv(db: Session = Depends(get_db)):

    if not all([os.path.exists(DEPARTMENTS_FILE_PATH), os.path.exists(JOBS_FILE_PATH), os.path.exists(EMPLOYEES_FILE_PATH)]):
        return {"error": "One or more CSV files are missing from the specified paths."}

    departments = set()

    with open(DEPARTMENTS_FILE_PATH, mode='r', encoding='utf-8') as departments_file:
        data = departments_file.readlines()
        reader = csv.reader(data)
        for row in reader:
            departments.add(row[1]) 

    departments_to_insert = [Department(name=dept) for dept in departments]
    db.bulk_save_objects(departments_to_insert)

    jobs = set()

    with open(JOBS_FILE_PATH, mode='r', encoding='utf-8') as jobs_file:
        data = jobs_file.readlines()
        reader = csv.reader(data)
        for row in reader:
            jobs.add(row[1])  

    jobs_to_insert = [Job(title=job) for job in jobs]
    db.bulk_save_objects(jobs_to_insert)
    
    db.commit()  

    employees_to_insert = []

    with open(EMPLOYEES_FILE_PATH, mode='r', encoding='utf-8') as employees_file:
        data = employees_file.readlines()
        reader = csv.reader(data)
        for row in reader:
            employee_name = row[1]
            hired_at = row[2]
            department_id = row[3]
            job_id = row[4]

            if hired_at and job_id and department_id:
                try:
                    department_id = int(department_id)
                    job_id = int(job_id)
                    employees_to_insert.append(Employee(
                        name=employee_name,
                        hired_at=hired_at,
                        department_id=department_id,
                        job_id=job_id
                    ))
                except ValueError:
                    continue 

    db.bulk_save_objects(employees_to_insert)
    db.commit()  

    num_departments = len(departments_to_insert)
    num_jobs = len(jobs_to_insert)
    num_employees = len(employees_to_insert)

    return {
        "message": f"Successfully uploaded {num_departments} departments, {num_jobs} jobs, and {num_employees} employees."
    }