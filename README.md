# Max GPA Calculator Project
# Authors: Ben Elster, Ryder Gilman, Reed Nystrom, Harrison Ramos, Nate Wong
# Date: May 5, 2026
# Course: CS 422 Software Methodologies
# Description: Flask-based web application for calculating current and maximum possible GPA using degree requirements and grade data.

---

## 1. Project Description

The Max GPA Calculator is a web-based system that allows students to:
- Enter completed coursework and grades
- View their current GPA
- Calculate maximum possible GPA based on remaining coursework
- Use degree requirement data to improve accuracy
- Generate PDF reports of GPA results

The system is designed to support academic planning and decision-making for students.

---

## 2. How to Run the Program

### Requirements
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. Extract the project zip file
2. Open a terminal in the project directory
3. Create a virtual environment:

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

Before running the application and using the admin interface, all CSV data files must be placed in the correct directories.

- Degree requirement CSV files → degree_data/
- Historical grade CSV files → grade_data/

Example Structure:
degree_data/
    cs_degree.csv

grade_data/
    grades_2018_2024.csv


### Running the Application

With the virtual environment activated, run:
```bash
python backend/app.py
```

The application will start on `http://127.0.0.1:5000`
---

## 3. Software Dependencies

- Python 3.8+
- Flask
- SQLite3
- pandas (if used in CSV processing)
- reportlab (for PDF generation)

All dependencies are listed in `requirements.txt`.

---

## 4. Directory Structure
```
CS-422-Max-GPA-Project/
│
├── backend/
│ ├── app.py # Main Flask application
│ ├── csv_parser.py # Handles CSV data processing
│ ├── db.py # Database connection logic
│ ├── models.py # Data models and GPA logic
│ ├── pdf_generator.py # Generates GPA PDF reports
│ ├── schema.sql # Database schema setup
│ └── static/
│ └── stylemain.css # CSS styling
│
├── frontend/
│ └── templates/
│ ├── index.html # Home page
│ ├── student.html # Student interface
│ └── admin.html # Admin interface
│
├── degree_data/ # Degree requirement CSV files
├── grade_data/ # Historical grade datasets
├── Reconciliation.csv # Supporting dataset
├── requirements.txt # Python dependencies
└── README.txt # This file
```

---

## 5. System Overview

### Backend
The backend is implemented using Flask and handles:
- GPA calculations
- Data parsing from CSV files
- Database operations
- Report generation

### Frontend
The frontend uses HTML templates to provide:
- Student interface for GPA calculation
- Admin interface for data management

### Data Processing
The system uses CSV files containing:
- Degree requirements
- Historical grade data

These are parsed and used to compute GPA values.

---

## 6. Usage Instructions

### Admin Setup (Required First)
1. Ensure CSV files are placed in the correct directories:
- degree_data/
- grade_data/
2. Upload or update CSV data files through the admin interface
3. Confirm data is successfully loaded
4. Maintain dataset consistency

### Student Mode
1. Navigate to the student interface
2. Select a degree program
3. Select a year range
4. Click “Download PDF”
5. View generated report

### Expected Output:
A pdf containing:
- Couse grade distributions
- Instrutor statistics
- Historical performance insights
---
