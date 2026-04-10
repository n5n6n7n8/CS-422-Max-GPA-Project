# CS-422-Max-GPA-Project

Max GPA Calculator - A Flask web application to calculate maximum GPA.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CS-422-Max-GPA-Project
```

2. Create and activate a virtual environment:

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

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

With the virtual environment activated, run:
```bash
python backend/app.py
```

The application will start on `http://127.0.0.1:5000`

### Project Structure
```
├── backend/
│   └── app.py          # Flask application
├── frontend/
│   └── templates/
│       └── index.html  # HTML template
├── requirements.txt    # Python dependencies
└── README.md          # This file
```
