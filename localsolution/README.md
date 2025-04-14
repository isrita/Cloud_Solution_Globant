# DB Migration API

This is a FastAPI application that handles database migrations by uploading historical data from CSV files to a SQL database.

## Features
- Receives CSV files containing data for departments, jobs, and employees.
- Uploads data to a MySQL database.
- Supports batch transactions of up to 1000 records in a single request.

## Setup

1. Clone the repository.
2. Create a virtual environment:
    ```bash
    python -m venv venv
    ```
3. Activate the virtual environment:
    ```bash
    .\venv\Scripts\Activate 
    ```
4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Start the FastAPI app:
    ```bash
    uvicorn main:app --reload
    ```

## API Endpoints
- **POST /upload/**: Upload a CSV file containing employee data.

## Database Schema
- **Departments**: Stores department names.
- **Jobs**: Stores job titles.
- **Employees**: Stores employee data, linking to departments and jobs.
