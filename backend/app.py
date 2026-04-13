import os
from io import BytesIO

from flask import Flask, render_template, request, send_file

from pdf_generator import generate_pdf_bytes

template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'templates')
app = Flask(__name__, template_folder=template_folder)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download-report')
def download_report():
    degree_id = request.args.get('degree_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)

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