# Resume Screening Assistant

A Flask-based application for recruiters to screen and match resumes with job requirements.

## Features

- User authentication (login/register) for recruiters
- Create and manage job postings
- Upload and analyze candidate resumes (PDF/DOCX formats)
- Automatic skill extraction and matching
- Candidate workflow management (New, Reviewing, Shortlisted, Rejected)

## Tech Stack

- Python 3.11
- Flask + Flask-Login + Flask-SQLAlchemy
- PostgreSQL or SQLite database
- PyPDF2 and docx2txt for document parsing
- spaCy for natural language processing
- Bootstrap for front-end styling

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install spaCy model: `python -m spacy download en_core_web_sm`
4. Set environment variables:
   - `SESSION_SECRET` for Flask session encryption
   - `DATABASE_URL` for database connection (optional, defaults to SQLite)
5. Run the application: `python main.py`

## Usage

1. Register for a recruiter account
2. Create a job posting with requirements
3. Upload candidate resumes
4. View matched candidates ranked by compatibility
5. Update candidate status as they progress through your recruitment process

## Setup for Development

### Database Setup
The application uses SQLAlchemy and can work with both SQLite (default) and PostgreSQL databases.

For SQLite (default, no configuration needed):
- Database will be created automatically at `instance/resume_assistant.db`

For PostgreSQL:
- Set the `DATABASE_URL` environment variable:
