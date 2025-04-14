from fastapi import FastAPI
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import ResourceExistsError
import csv
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TENANT_ID = "************************************"
CLIENT_ID = "************************************"
CLIENT_SECRET = "****************************************"

STORAGE_ACCOUNT_NAME = "datalakegen2israel"
BLOB_CONTAINER_NAME = "globantfiles"
FILE_SYSTEM_NAME = "globantfiles"

credential = ClientSecretCredential(
    tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)

blob_service = BlobServiceClient(
    account_url=f"https://blobstorageisrael.blob.core.windows.net", credential=credential
)
datalake_account_url = f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net"
datalake_service = DataLakeServiceClient(account_url=datalake_account_url, credential=credential)

filesystem_client = datalake_service.get_file_system_client(FILE_SYSTEM_NAME)

directory_client = filesystem_client.get_directory_client("bronze")
try:
    directory_client.create_directory()
except ResourceExistsError:
    pass

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "FastAPI for migrating CSVs from Blob to Data Lake Gen2"}


def read_blob_csv(blob_name: str):
    logger.info(f"Reading blob file: {blob_name}")
    blob_client = blob_service.get_blob_client(container=BLOB_CONTAINER_NAME, blob=blob_name)
    stream = blob_client.download_blob()
    return csv.reader(io.StringIO(stream.readall().decode("utf-8")))


def upload_text_file_to_datalake(filename: str, content: str):
    logger.info(f"Uploading {filename} to Data Lake bronze/")
    file_client = directory_client.get_file_client(filename)
    file_client.upload_data(content.encode("utf-8"), overwrite=True)
    logger.info(f"{filename} uploaded successfully")


@app.post("/upload/")
async def upload_csv():
    departments_blob = "departments.csv"
    jobs_blob = "jobs.csv"
    employees_blob = "hired_employees.csv"

    # Procesar departments.csv
    departments = set()
    for row in read_blob_csv(departments_blob):
        departments.add(f"{row[0]}: {row[1]}")

    upload_text_file_to_datalake("departments.csv", "\n".join(departments))

    # Procesar jobs.csv
    jobs = set()
    for row in read_blob_csv(jobs_blob):
        jobs.add(f"{row[0]}: {row[1]}")

    upload_text_file_to_datalake("jobs.csv", "\n".join(jobs))

    # Procesar hired_employees.csv
    employees = []
    for row in read_blob_csv(employees_blob):
        if len(row) >= 5:
            employees.append(f"{row[0]}: {row[1]}")

    upload_text_file_to_datalake("employees.csv", "\n".join(employees))

    return {
        "message": f"Uploaded {len(departments)} departments, {len(jobs)} jobs, {len(employees)} employees to bronze/"
    }
