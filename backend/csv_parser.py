"""
Ryder Gilman
CSV Parser for MAXGPA 
Last edited April 9th 


If testing to see what sample prints are, run 
python src/csv_parser.py


April 9th:
The initial csv_parser.py has been added to the project

This file: 
reads raw uo grade CSV and converts each row into a normalized python dict
converts * to NULL
provides aggregation helpers for course level and course+instructor level summaries

-------------------
After loading the file, each class becomes a python dict with fields like:

term_code, term_desc, season_term, 
calendar_year, academic_year, subj, 
numb, course_key, title, crn, 
instructor_name, offering_count, 
student_count, display_denominator, grade_buckets 
(A/B/C/DNF/P/W), cleaned_grades (raw columns)

-------------------
A single row looks like this:
{'term_code': '201601', 'term_desc': 'Fall 2016', 'season_term': 'fall', 
'calendar_year': 2016, 'academic_year': 'AY16', 'subj': 'CIS', 
'numb': '210', 'raw_course_key': 'CIS 210', 'course_key': 'CS 210', 
'title': 'Computer Science I', 'crn': '11539', 
'instructor_name': 'Sventek, Joseph Sherman', 
'offering_count': 1, 'student_count': 141, 
'display_denominator': 137, 
'grade_buckets': {'A': 31, 'B': 45, 'C': 35, 'DNF': 26, 'P': 4, 'W': 8}, 
'cleaned_grades': {'AP': 3, 'A': 12, 'AM': 16, 'BP': 14, 'B': 16, 'BM': 15, 'CP': 13, 'C': 12, 'CM': 10, 'DP': 5, 'D': 5, 'DM': 2, 'F': 1, 'P': 4, 'N': 13, 'OTHER': 0, 'W': 8}
}

--------------------




"""
import csv


GRADE_COLUMNS = [
    "AP", "A", "AM",
    "BP", "B", "BM",
    "CP", "C", "CM",
    "DP", "D", "DM",
    "F", "P", "N", "OTHER", "W"
]

# Asked claude to find all courses with "CIS" prefix 
# and map to "CS" for normalization
# 2016-2022 has courses like "CIS 210" that are the same as "CS 210" in 2023-2024
COURSE_ALIASES = {
    "CIS 102": "CS 102",
    "CIS 110": "CS 110",
    "CIS 111": "CS 111",
    "CIS 122": "CS 122",
    "CIS 210": "CS 210",
    "CIS 211": "CS 211",
    "CIS 212": "CS 212",
    "CIS 313": "CS 313",
    "CIS 314": "CS 314",
    "CIS 315": "CS 315",
    "CIS 322": "CS 322",
    "CIS 330": "CS 330",
    "CIS 333": "CS 333",
    "CIS 372M": "CS 372M",
    "CIS 413": "CS 413",
    "CIS 415": "CS 415",
    "CIS 420": "CS 420",
    "CIS 422": "CS 422",
    "CIS 423": "CS 423",
    "CIS 425": "CS 425",
    "CIS 429": "CS 429",
    "CIS 431": "CS 431",
    "CIS 432": "CS 432",
    "CIS 433": "CS 433",
    "CIS 436": "CS 436",
    "CIS 441": "CS 441",
    "CIS 443": "CS 443",
    "CIS 445": "CS 445",
    "CIS 451": "CS 451",
    "CIS 453": "CS 453",
    "CIS 461": "CS 461",
    "CIS 471": "CS 471",
    "CIS 472": "CS 472",
    "CIS 473": "CS 473",
}

def apply_course_alias(course_key):
    return COURSE_ALIASES.get(course_key, course_key)



def clean_cell(value):
    """Convert blank values and '*' into None"""
    if value is None:
        return None
    value = value.strip()
    if value == "" or value == "*":
        return None
    return value



def to_int_or_zero(value):
    """Convert a cleaned value into int, using 0 for None."""
    if value is None:
        return 0
    return int(value)


def normalize_text(value, fallback=""):
    """Clean a text field and return a fallback if missing."""
    value = clean_cell(value)

    if value is None:
        return fallback
    
    return value.strip()


def normalize_instructor_name(name):
    """Normalize instructor names for grouping."""
    cleaned_name = normalize_text(name)
    if cleaned_name == "":
        return "Unknown"
    return cleaned_name


def parse_term_desc(term_desc):
    """Extract season_term and calendar_year from TERM_DESC"""
    cleaned_term_desc = normalize_text(term_desc)

    if cleaned_term_desc == "":
        return None, None

    parts = cleaned_term_desc.split()

    season_term = None
    calendar_year = None

    for part in parts:
        lower_part = part.lower()

        if lower_part in ["fall", "winter", "spring", "summer"]:
            season_term = lower_part

        if part.isdigit() and len(part) == 4:
            calendar_year = int(part)

    return season_term, calendar_year


def derive_academic_year_label(season_term, calendar_year):
    """
    Academic year starts in fall:
    Fall 2016   -> AY16
    Winter 2017 -> AY16
    Spring 2017 -> AY16
    Summer 2017 -> AY16
    """
    if season_term is None or calendar_year is None:
        return None

    if season_term == "fall":
        ay_start_year = calendar_year
    else:
        ay_start_year = calendar_year - 1

    short_year = str(ay_start_year)[-2:]
    return "AY" + short_year


def academic_year_in_supported_range(academic_year):
    """Keep only AY16 through AY23."""
    supported_years = {
        "AY16", "AY17", "AY18", "AY19",
        "AY20", "AY21", "AY22", "AY23"
    }

    return academic_year in supported_years


def clean_grade_columns(row):
    """Convert raw grade columns into cleaned integers/None."""
    cleaned_grades = {}

    for column_name in GRADE_COLUMNS:
        cleaned_value = clean_cell(row.get(column_name))

        if cleaned_value is None:
            cleaned_grades[column_name] = None
        else:
            cleaned_grades[column_name] = int(cleaned_value)

    return cleaned_grades


def collapse_grade_buckets(cleaned_grades):
    """Collapse raw grade columns into display buckets."""
    a_bucket = (
        to_int_or_zero(cleaned_grades.get("AP")) +
        to_int_or_zero(cleaned_grades.get("A")) +
        to_int_or_zero(cleaned_grades.get("AM"))
    )

    b_bucket = (
        to_int_or_zero(cleaned_grades.get("BP")) +
        to_int_or_zero(cleaned_grades.get("B")) +
        to_int_or_zero(cleaned_grades.get("BM"))
    )

    c_bucket = (
        to_int_or_zero(cleaned_grades.get("CP")) +
        to_int_or_zero(cleaned_grades.get("C")) +
        to_int_or_zero(cleaned_grades.get("CM"))
    )

    dnf_bucket = (
        to_int_or_zero(cleaned_grades.get("DP")) +
        to_int_or_zero(cleaned_grades.get("D")) +
        to_int_or_zero(cleaned_grades.get("DM")) +
        to_int_or_zero(cleaned_grades.get("F")) +
        to_int_or_zero(cleaned_grades.get("N")) +
        to_int_or_zero(cleaned_grades.get("OTHER"))
    )

    p_bucket = to_int_or_zero(cleaned_grades.get("P"))
    w_bucket = to_int_or_zero(cleaned_grades.get("W"))

    return {
        "A": a_bucket,
        "B": b_bucket,
        "C": c_bucket,
        "DNF": dnf_bucket,
        "P": p_bucket,
        "W": w_bucket
    }


def compute_display_denominator(grade_buckets):
    """
    Use A + B + C + DNF for normal classes.
    If that is 0, fall back to P + DNF for pass/fail-only cases.
    """
    letter_grade_total = (
        grade_buckets["A"] +
        grade_buckets["B"] +
        grade_buckets["C"] +
        grade_buckets["DNF"]
    )

    if letter_grade_total > 0:
        return letter_grade_total

    return grade_buckets["P"] + grade_buckets["DNF"]


def build_course_key(subj, numb):
    """Create a temporary course key like 'CS 210'."""
    cleaned_subj = normalize_text(subj)
    cleaned_numb = normalize_text(numb)
    return (cleaned_subj + " " + cleaned_numb).strip()


def normalize_row(raw_row):
    """Convert one raw CSV row into one normalized row."""
    term_desc = raw_row.get("TERM_DESC")

    season_term, calendar_year = parse_term_desc(term_desc)
    academic_year = derive_academic_year_label(season_term, calendar_year)

    if not academic_year_in_supported_range(academic_year):
        return None

    term_code = normalize_text(raw_row.get("TERM"))
    subj = normalize_text(raw_row.get("SUBJ"))
    numb = normalize_text(raw_row.get("NUMB"))
    title = normalize_text(raw_row.get("TITLE"))
    crn = normalize_text(raw_row.get("CRN"))
    instructor_name = normalize_instructor_name(raw_row.get("INSTRUCTOR"))

    raw_course_key = build_course_key(subj, numb)
    course_key = apply_course_alias(raw_course_key)

    cleaned_grades = clean_grade_columns(raw_row)
    grade_buckets = collapse_grade_buckets(cleaned_grades)

    tot_non_w = clean_cell(raw_row.get("TOT_NON_W"))
    student_count = to_int_or_zero(tot_non_w)
    offering_count = 1
    display_denominator = compute_display_denominator(grade_buckets)

    return {
        "term_code": term_code,
        "term_desc": normalize_text(term_desc),
        "season_term": season_term,
        "calendar_year": calendar_year,
        "academic_year": academic_year,
        "subj": subj,
        "numb": numb,
        "raw_course_key": raw_course_key,
        "course_key": course_key,
        "title": title,
        "crn": crn,
        "instructor_name": instructor_name,
        "offering_count": offering_count,
        "student_count": student_count,
        "display_denominator": display_denominator,
        "grade_buckets": grade_buckets,
        "cleaned_grades": cleaned_grades
    }


def load_grade_data_from_csv(csv_path):
    """Read a CSV of grade history data and return normalized rows."""
    normalized_rows = []

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for raw_row in reader:
            normalized = normalize_row(raw_row)

            if normalized is not None:
                normalized_rows.append(normalized)

    return normalized_rows


def load_degree_data_from_csv(csv_path):
    """Read degree course data from CSV and return in format for models.create_degree"""
    degree_courses = []

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            year = int(row.get("YEAR", 0))
            term = int(row.get("TERM", 0))
            course_subj = normalize_text(row.get("SUBJ"))
            course_num = normalize_text(row.get("NUMB"))
            title = normalize_text(row.get("TITLE"))

            degree_courses.append({
                "year": year,
                "term": term,
                "course_subj": course_subj,
                "course_num": course_num,
                "title": title
            })

    return degree_courses


def aggregate_by_course(normalized_rows):
    """Aggregate normalized rows by course."""
    course_summary = {}

    for row in normalized_rows:
        course_key = row["course_key"]

        if course_key not in course_summary:
            course_summary[course_key] = {
                "course_key": course_key,
                "subj": row["subj"],
                "numb": row["numb"],
                "title": row["title"],
                "offering_count": 0,
                "student_count": 0,
                "display_denominator": 0,
                "A": 0,
                "B": 0,
                "C": 0,
                "DNF": 0,
                "P": 0,
                "W": 0
            }

        course_summary[course_key]["offering_count"] += row["offering_count"]
        course_summary[course_key]["student_count"] += row["student_count"]
        course_summary[course_key]["display_denominator"] += row["display_denominator"]

        course_summary[course_key]["A"] += row["grade_buckets"]["A"]
        course_summary[course_key]["B"] += row["grade_buckets"]["B"]
        course_summary[course_key]["C"] += row["grade_buckets"]["C"]
        course_summary[course_key]["DNF"] += row["grade_buckets"]["DNF"]
        course_summary[course_key]["P"] += row["grade_buckets"]["P"]
        course_summary[course_key]["W"] += row["grade_buckets"]["W"]

    return course_summary


def aggregate_by_course_and_instructor(normalized_rows):
    """Aggregate normalized rows by (course, instructor)."""
    summary = {}

    for row in normalized_rows:
        key = (row["course_key"], row["instructor_name"])

        if key not in summary:
            summary[key] = {
                "course_key": row["course_key"],
                "instructor_name": row["instructor_name"],
                "offering_count": 0,
                "student_count": 0,
                "display_denominator": 0,
                "A": 0,
                "B": 0,
                "C": 0,
                "DNF": 0,
                "P": 0,
                "W": 0
            }

        summary[key]["offering_count"] += row["offering_count"]
        summary[key]["student_count"] += row["student_count"]
        summary[key]["display_denominator"] += row["display_denominator"]

        summary[key]["A"] += row["grade_buckets"]["A"]
        summary[key]["B"] += row["grade_buckets"]["B"]
        summary[key]["C"] += row["grade_buckets"]["C"]
        summary[key]["DNF"] += row["grade_buckets"]["DNF"]
        summary[key]["P"] += row["grade_buckets"]["P"]
        summary[key]["W"] += row["grade_buckets"]["W"]

    return summary


def compute_a_rate(record):
    """Compute A rate using display_denominator """
    denominator = record["display_denominator"]

    if denominator == 0:
        return 0.0

    return record["A"] / denominator


def print_sample_rows(normalized_rows, limit=3):
    """test row printing"""
    for row in normalized_rows[:limit]:
        print(row)
        print()


if __name__ == "__main__":
    csv_path = "backend/pub_rec_master_w2016-f2025.csv"

    normalized_rows = load_grade_data_from_csv(csv_path)

    print("Normalized rows:", len(normalized_rows))
    print()

    #print("Sample normalized rows:")
    #print_sample_rows(normalized_rows, limit=3)

    cs_210_rows = [row for row in normalized_rows if row["course_key"] == "CS 210"]

    for row in cs_210_rows:
        print(row)
        print()
    