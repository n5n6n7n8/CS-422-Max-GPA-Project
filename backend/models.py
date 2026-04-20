from db import get_db

# Add a new degree program to DB w/ the given title and list of courses (rows from CSV)
# rows should be in the following format (example):
# [
#     {'year': 1, 'term': 1, 'course_subj': 'BA', 'course_num': '101Z', 'title': 'Intro to Business'},
#     ...
# ]
def create_degree(degree_title, rows):
    db = get_db()
    existing_degree = False

    # If degree_title is already in table, get degree_id, else create new degree and get degree_id
    degree_id = db.execute("SELECT degree_id FROM degree WHERE degree_title = ?", (degree_title,)).fetchone()
    if degree_id is None:
        degree_id = db.execute("INSERT INTO degree (degree_title) VALUES (?)", (degree_title,)).lastrowid
    else:
        existing_degree = True
        degree_id = degree_id['degree_id']
    
    # Delete existing courses for this degree
    db.execute("DELETE FROM degree_courses WHERE degree_id = ?", (degree_id,))

    inserted_count = 0
    for row in rows:
        year = row['year']
        term = row['term']
        course_key = f"{row['course_subj']} {row['course_num']}"
        course_title = row['title']
        
        cursor =db.execute(
            "INSERT OR IGNORE INTO degree_courses (degree_id, year, term, course_key, course_title) VALUES (?, ?, ?, ?, ?)",
            (degree_id, year, term, course_key, course_title)
        )
        inserted_count += cursor.rowcount
    db.commit()

    # Return whether degree already existed and how many courses were inserted
    return existing_degree, inserted_count


# Insert grade data into the database, replacing existing data
# Use the output of csv_parser.load_normalized_rows as input for this function
def insert_grade_data(normalized_rows):
    db = get_db()
    inserted_count = 0

    # Delete existing data
    db.execute("DELETE FROM grade_history")

    for row in normalized_rows:
        term_code = row['term_code']
        course_key = row['course_key']
        instructor_name = row['instructor_name']
        academic_year = row['academic_year']
        crn = row['crn']
        a_count = row['grade_buckets']['A']
        b_count = row['grade_buckets']['B']
        c_count = row['grade_buckets']['C']
        dnf_count = row['grade_buckets']['DNF']

        cursor = db.execute(
            "INSERT OR IGNORE INTO grade_history (term_code, course_key, instructor_name, academic_year, crn, a_count, b_count, c_count, dnf_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (term_code, course_key, instructor_name, academic_year, crn, a_count, b_count, c_count, dnf_count)
        )
        inserted_count += cursor.rowcount
    db.commit()
    return inserted_count


# Get academic years available in the grade_history table
def get_academic_years():
    db = get_db()
    rows = db.execute("SELECT DISTINCT academic_year FROM grade_history ORDER BY academic_year ASC").fetchall()
    return [row['academic_year'] for row in rows]


# Get list of (degree_id, degree_title) for all degree programs in the DB
def get_degrees():
    db = get_db()
    rows = db.execute("SELECT degree_id, degree_title FROM degree").fetchall()
    return [(row['degree_id'], row['degree_title']) for row in rows]