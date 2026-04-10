import os
from flask import Flask, render_template

template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'templates')
app = Flask(__name__, template_folder=template_folder)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)