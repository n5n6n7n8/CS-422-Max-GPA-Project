# Max GPA Calculator Project
# Authors: Ben Elster, Ryder Gilman, Reed Nystrom, Harrison Ramos, Nate Wong
# Date: May 4, 2026
# Course: CS 422 Software Methodologies
# Description: Flask-based web application for plotting historical grade data to assist UO students in planning their classes to maximize their GPA.

---

## 1. Project Description

The Max GPA Calculator is a web-based system that allows students to:
- Calculate estimated GPA based on historical grade data
- See which instructors give the highest grades for their required courses

The system is designed to support academic planning and decision-making for students.

---

## 2. Documentation

This file only describes basic requirements and installation. For the full user documentation (admin setup & student use), please view [User_Documentation.pdf](User_Documentation.pdf).

We also provide the following technical documentation:
- [Project_Plan_and_SDS.pdf](Project_Plan_and_SDS.pdf)
- [Programmers_Documentation.pdf](Programmers_Documentation.pdf)

---

## 3. How to Run the Program

### Requirements
- Python 3.8 or higher
- pip package manager

### Installation Instructions

1. Extract the project zip file
2. Open a terminal in the project directory
3. Create a virtual environment by running these terminal commands:

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




### Running the Application

With the virtual environment activated, run this terminal command:
```bash
python backend/app.py
```

Once the app launches, navigate to `http://127.0.0.1:5000` in your web browser to view the web interface.

Before using the admin interface, all CSV data files must be placed in the correct directories.

- Degree requirement CSV files → `degree_data/`
- Historical grade CSV files → `grade_data/`

Example Structure:
```
degree_data/
    cs_degree.csv

grade_data/
    grades_2018_2024.csv
```

View more detailed instructions for CSV formatting & uploading in [User_Documentation.pdf](User_Documentation.pdf).

---


## 4. Directory Structure
```
CS-422-Max-GPA-Project/
│
├── backend/
│ ├── app.py # Main Flask application
│ ├── csv_parser.py # Handles CSV data processing
│ ├── db.py # Database connection logic
│ ├── models.py # Helper functions for DB queries
│ ├── pdf_generator.py # Generates PDF reports w/ grade plots
│ ├── schema.sql # SQLite database schema
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
├── grade_data/ # Historical grade CSV files
├── Reconciliation.csv # Config for normalizing course keys
├── requirements.txt # Python dependencies
└── README.md # This file
```

---

## 5. System Overview

### Backend
The backend is implemented using Flask and handles:
- Grade distribution calculations
- Data parsing from CSV files
- Database operations
- PDF Report generation

### Frontend
The frontend uses HTML templates to provide:
- Student interface for generating grade distribution reports
- Admin interface for data management

### Data Processing
The system uses CSV files containing:
- Degree requirements
- Historical grade data

These are parsed and used to compute grade distributions across required courses for a degree.

---

## 6. Usage Instructions

Please refer to [User_Documentation.pdf](User_Documentation.pdf) for usage instructions.
