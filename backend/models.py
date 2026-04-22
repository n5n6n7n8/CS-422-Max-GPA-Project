from db import get_db

# (A, B, C, DNF) counts for a single course & instructor (or all instructors for a course)
GradeCounts = tuple[int, int, int, int]
# (Instructor Name, GradeCounts) for a single course
InstructorDistribution = tuple[str, GradeCounts]
# Term -> Course -> List of (Instructor Name, GradeCounts)
TermCourseData = dict[str, dict[str, list[InstructorDistribution]]]


# Delete everything from degree and degree_courses tables
def clear_degrees():
    db = get_db()
    db.execute("DELETE FROM degree_courses")
    db.execute("DELETE FROM degree")
    db.commit()


# Add a new degree program to DB w/ the given title and list of courses (rows from CSV).
# Use the output of csv_parser.load_degree_data_from_csv as input for this function.
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
# Use the output of csv_parser.load_grade_data_from_csv as input for this function
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


# Takes a degree & year range, queries DB for grade data of courses that degree & year range,
# and returns that data in the form of a TermCourseData object.
def get_term_course_data(degree_id, year_from, year_to):
    db = get_db()
    rows = db.execute(
        """
        SELECT dc.year, dc.term, dc.course_key, dc.course_title, gh.instructor_name, gh.a_count, gh.b_count, gh.c_count, gh.dnf_count
        FROM degree_courses dc
        JOIN grade_history gh ON dc.course_key = gh.course_key
        WHERE dc.degree_id = ? AND gh.academic_year BETWEEN ? AND ?
        """,
        (degree_id, year_from, year_to)
    ).fetchall()

    # print(len(rows))

    term_course_data: TermCourseData = {}
    for row in rows:
        year = row['year']
        term = row['term']
        course_key = f"{row['course_key']} - {row['course_title']}"
        instructor_name = row['instructor_name']
        grade_counts = (row['a_count'], row['b_count'], row['c_count'], row['dnf_count'])

        term_str = f"Year {year} - Term {term}"
        if term_str not in term_course_data:
            term_course_data[term_str] = {}
        
        if course_key not in term_course_data[term_str]:
            term_course_data[term_str][course_key] = []
        
        # If instructor already exists for this course, add grade counts to existing counts
        instructor_found = False
        for i, (old_instructor, old_counts) in enumerate(term_course_data[term_str][course_key]):
            if old_instructor == instructor_name:
                new_counts = tuple(existing + new for existing, new in zip(old_counts, grade_counts))
                term_course_data[term_str][course_key][i] = (old_instructor, new_counts)
                instructor_found = True
                break
        # Otherwise, add the new instructor & grade counts
        if not instructor_found:
            term_course_data[term_str][course_key].append((instructor_name, grade_counts))
    
    return term_course_data