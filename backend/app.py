import os
from io import BytesIO
import click

from flask import Flask, jsonify, render_template, request, send_file

from db import close_db
from pdf_generator import generate_pdf_bytes

template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'templates')
app = Flask(__name__, template_folder=template_folder)
app.config["DATABASE"] = "database.db"
app.teardown_appcontext(close_db)


# Homepage route
@app.route('/')
def index():
    return render_template('index.html')


# Student page route
@app.route('/student')
def student():
    from models import get_academic_years, get_degrees
    return render_template('student.html', years=get_academic_years(), degrees=get_degrees())


# Admin page route
@app.route('/admin')
def admin():
    from models import get_available_grade_csv_files, get_available_degree_csv_files
    return render_template('admin.html', grade_csvs=get_available_grade_csv_files(), degree_csvs=get_available_degree_csv_files())


# Route for generating & displaying PDF on-the-fly based on selected degree & year range
@app.route('/download-report')
def download_report():
    degree_id = request.args.get('degree_id', type=int)
    year_from = request.args.get('year_from', type=str)
    year_to = request.args.get('year_to', type=str)

    if (degree_id is None) or (year_from is None) or (year_to is None):
        return "ERROR: Missing required query parameters", 400
    pdf_bytes = generate_pdf_bytes(degree_id, year_from, year_to)

    return send_file(
        BytesIO(pdf_bytes),
        as_attachment=False,
        download_name='degree_report.pdf',
        mimetype='application/pdf',
    )


# API endpoint for getting sample row data from grade CSV.
# Used for previewing data on frontend for confirmation
@app.route('/api/grade-sample-row', methods=['GET'])
def grade_sample_row():
    grade_csv = request.args.get('csv', type=str)
    if grade_csv is None:
        return "ERROR: Missing required parameter 'csv'", 400

    from csv_parser import load_sample_grade_row
    sample = load_sample_grade_row(f"grade_data/{grade_csv}")
    success = isinstance(sample, dict)
    return jsonify({"success": success, "payload": sample})


# API endpoint for getting sample row data from degree CSV.
# Used for previewing data on frontend for confirmation
@app.route('/api/degree-sample-row', methods=['GET'])
def degree_sample_row():
    degree_csv = request.args.get('csv', type=str)
    if degree_csv is None:
        return "ERROR: Missing required parameter 'csv'", 400

    from csv_parser import load_sample_degree_row
    sample = load_sample_degree_row(f"degree_data/{degree_csv}")
    success = isinstance(sample, dict)
    return jsonify({"success": success, "payload": sample})


# API endpoint for uploading grade data from CSV and inserting into database
@app.route('/api/upload-grades', methods=['POST'])
def upload_grade():
    data = request.get_json()
    csv_path = data.get('csv')

    from models import insert_grade_data
    from csv_parser import load_grade_data_from_csv

    try:
        rows = load_grade_data_from_csv(f"grade_data/{csv_path}")
        insert_count = insert_grade_data(rows)
        return jsonify({"success": True, "message": f"Inserted {insert_count} grade data rows from CSV into the database."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing grade data: {str(e)}"}), 500


# API endpoint for uploading degree data from CSV and inserting into database
@app.route('/api/upload-degree', methods=['POST'])
def upload_degree():
    data = request.get_json()
    degree_title = data.get('degree_title')
    csv_path = data.get('csv')

    from models import create_or_update_degree
    from csv_parser import load_degree_data_from_csv

    try:
        rows = load_degree_data_from_csv(f"degree_data/{csv_path}")
        existing_degree, insert_count = create_or_update_degree(degree_title, rows)

        if existing_degree:
            return jsonify({
                "success": True,
                "message": f"Successfully updated degree program '{degree_title}' with {insert_count} courses."})
        else:
            return jsonify({
                "success": True,
                "message": f"Successfully created degree program '{degree_title}' with {insert_count} courses."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing degree data: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=False)