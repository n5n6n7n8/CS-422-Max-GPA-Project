import os
from io import BytesIO
import click

from flask import Flask, render_template, request, send_file

from db import close_db
from models import insert_grade_data
from pdf_generator import generate_pdf_bytes

template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'templates')
app = Flask(__name__, template_folder=template_folder)
app.config["DATABASE"] = "database.db"
app.teardown_appcontext(close_db)


# Command line command to load grade data from a CSV file into the database
# We'll change this to an endpoint later on to hook it up to the frontend
@app.cli.command('load-grade-data')
@click.argument('csv_path')
def load_grade_data(csv_path):
    from csv_parser import load_grade_data_from_csv
    normalized_rows = load_grade_data_from_csv(csv_path)
    insert_count = insert_grade_data(normalized_rows)
    click.echo(f"Loaded {insert_count} rows into the database.")


# Command line command to add degree program to DB w/ data from CSV
# This is just some sample code to test out the DB operations
@app.cli.command('create-degree')
@click.argument('degree_title')
@click.argument('csv_path')
def create_degree(degree_title, csv_path):
    from models import create_degree
    from csv_parser import load_degree_data_from_csv

    rows = load_degree_data_from_csv(csv_path)
    existing_degree, insert_count = create_degree(degree_title, rows)

    if existing_degree:
        click.echo(f"Updated degree program '{degree_title}' with {insert_count} courses.")
    else:
        click.echo(f"Created degree program '{degree_title}' with {insert_count} courses.")


# Test command to get academic years available in grade history table
@app.cli.command('get-ays')
def get_academic_years():
    from models import get_academic_years
    ays = get_academic_years()
    click.echo(f"Academic years in grade history: {ays}")

# Test command to get degrees available in degree table
@app.cli.command('get-degrees')
def get_degrees():
    from models import get_degrees
    degrees = get_degrees()
    click.echo(f"Degrees in degree table: {degrees}")

# Test command to clear degree and degree_courses tables
@app.cli.command('clear-degrees')
def clear_degrees_command():
    from models import clear_degrees
    clear_degrees()
    click.echo("Cleared degree and degree_courses tables.")


@app.route('/')
def index():
    return render_template('index.html')


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

if __name__ == '__main__':
    app.run(debug=True)