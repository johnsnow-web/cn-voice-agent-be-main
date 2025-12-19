# Inventory AI Agent

This project is an Inventory Management System (IMS) powered by AI.

## Steps to Set Up

### 1. Prerequisites
- Python 3.9 or greater
- PostgreSQL

### 2. Clone the Repository
```bash
git clone https://github.com/ciphernutz-team/cn-voice-agent-be.git
cd cn-voice-agent-be
```


### 3. Create and Activate Virtual Environment
```bash
python3 uv venv  #uv package manager
source .venv\Scripts\activate #Windows
source .venv/bin/activate #Linux
```



### 4. Install Dependencies
```bash
uv pip install -r requirement.txt
```

### 5. Create Database in PostgreSQL
Create a database in PostgreSQL for the project.

### 6. Create `.env` File
Create a `.env` file in the project root and add the following database configuration:
```
DB_NAME=*
DB_USER=*
DB_PASSWORD=*
DB_HOST=*
DB_PORT=*
```

### 7. Run Migrations
```bash
python manage.py migrate inventory
```

### 8. Seed Data (Optional)
```bash
python manage.py seed_data
```

### 9. Run the Server
```bash
python manage.py runserver
```

You can now access the application at `http://127.0.0.1:8000/`.
