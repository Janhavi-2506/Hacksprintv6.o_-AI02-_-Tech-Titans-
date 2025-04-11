import os
import logging
from flask import render_template, redirect, url_for, request, flash, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Resume, JobPosting, Candidate
from resume_processor import ResumeProcessor

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/test')
def test():
    """Test route to verify application is working."""
    return "Resume Screening Assistant API is working!"

@app.route('/')
def index():
    """Homepage route with simplified template rendering."""
    try:
        # Create a simple temporary index.html in the static folder
        temp_path = os.path.join(app.static_folder, 'temp_index.html')
        with open(temp_path, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Resume Screening Assistant</title>
                <style>
                    body {
                        background-color: #212529;
                        color: #f8f9fa;
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 50px;
                    }
                    h1 {
                        color: #0d6efd;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Resume Screening Assistant</h1>
                    <p>Streamline your recruitment process with AI-powered resume screening</p>
                    <p>This is a simplified page for troubleshooting</p>
                    <p><a href="/test" style="color: #0d6efd;">Test Route</a></p>
                    <p><a href="/login" style="color: #0d6efd;">Login</a></p>
                    <p><a href="/register" style="color: #0d6efd;">Register</a></p>
                </div>
            </body>
            </html>
            """)
        
        # Return a redirect to the static file
        return redirect('/static/temp_index.html')
    except Exception as e:
        logging.error(f"Error in index route: {str(e)}")
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register route."""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return render_template('register.html')
            
        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken', 'danger')
            return render_template('register.html')
            
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logout route."""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route."""
    # Get job postings for the current recruiter
    job_postings = JobPosting.query.filter_by(recruiter_id=current_user.id).all()
    
    # Count candidates for each job posting
    job_stats = []
    for job in job_postings:
        total_candidates = Candidate.query.filter_by(job_posting_id=job.id).count()
        shortlisted = Candidate.query.filter_by(job_posting_id=job.id, status='Shortlisted').count()
        reviewing = Candidate.query.filter_by(job_posting_id=job.id, status='Reviewing').count()
        
        job_stats.append({
            'job': job,
            'total': total_candidates,
            'shortlisted': shortlisted,
            'reviewing': reviewing
        })
    
    return render_template('dashboard.html', job_stats=job_stats)

@app.route('/job/new', methods=['GET', 'POST'])
@login_required
def new_job():
    """Create a new job posting."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        location = request.form.get('location')
        
        # Validate required fields
        if not title or not description or not requirements:
            flash('Please fill out all required fields', 'danger')
            return redirect(url_for('new_job'))
            
        # Create new job posting
        new_job = JobPosting(
            title=title,
            description=description,
            requirements=requirements,
            location=location,
            recruiter_id=current_user.id
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        flash('Job posting created successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('job_posting.html', job=None)

@app.route('/job/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    """Edit an existing job posting."""
    job = JobPosting.query.get_or_404(job_id)
    
    # Check if the current user is the owner of this job posting
    if job.recruiter_id != current_user.id:
        flash('You do not have permission to edit this job posting', 'danger')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        job.title = request.form.get('title')
        job.description = request.form.get('description')
        job.requirements = request.form.get('requirements')
        job.location = request.form.get('location')
        
        db.session.commit()
        
        flash('Job posting updated successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('job_posting.html', job=job)

@app.route('/job/<int:job_id>/candidates')
@login_required
def view_candidates(job_id):
    """View candidates for a specific job posting."""
    job = JobPosting.query.get_or_404(job_id)
    
    # Check if the current user is the owner of this job posting
    if job.recruiter_id != current_user.id:
        flash('You do not have permission to view these candidates', 'danger')
        return redirect(url_for('dashboard'))
        
    # Get candidates for this job posting
    candidates = Candidate.query.filter_by(job_posting_id=job_id).order_by(Candidate.match_score.desc()).all()
    
    return render_template('candidates.html', job=job, candidates=candidates)

@app.route('/job/<int:job_id>/upload', methods=['GET', 'POST'])
@login_required
def upload_resume(job_id):
    """Upload a resume for a specific job posting."""
    job = JobPosting.query.get_or_404(job_id)
    
    # Check if the current user is the owner of this job posting
    if job.recruiter_id != current_user.id:
        flash('You do not have permission to upload resumes for this job posting', 'danger')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['resume']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        # Check if the file is allowed
        if file and allowed_file(file.filename):
            # Get candidate information from form
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            
            # Validate required fields
            if not name or not email:
                flash('Please fill out all required fields', 'danger')
                return redirect(request.url)
            
            # Create a secure filename
            filename = secure_filename(file.filename)
            
            # Create a unique path for this file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(file_path)
            
            # Process the resume
            resume_data = ResumeProcessor.process_resume(file, job.requirements)
            
            if not resume_data['success']:
                flash(f'Error processing resume: {resume_data["error"]}', 'danger')
                return redirect(request.url)
            
            # Create new candidate
            new_candidate = Candidate(
                name=name,
                email=email,
                phone=phone,
                match_score=resume_data['match_score'],
                job_posting_id=job_id
            )
            
            db.session.add(new_candidate)
            db.session.flush()  # Get the candidate ID before committing
            
            # Create new resume entry
            new_resume = Resume(
                filename=filename,
                file_path=file_path,
                content_text=resume_data['text'],
                skills=resume_data['skills_text'],
                education=resume_data['education'],
                experience=resume_data['experience'],
                candidate_id=new_candidate.id
            )
            
            db.session.add(new_resume)
            db.session.commit()
            
            flash('Resume uploaded and processed successfully!', 'success')
            return redirect(url_for('view_candidates', job_id=job_id))
        else:
            flash('Allowed file types are PDF and DOCX', 'danger')
            return redirect(request.url)
            
    return render_template('upload_resume.html', job=job)

@app.route('/candidate/<int:candidate_id>')
@login_required
def view_candidate(candidate_id):
    """View a specific candidate's details."""
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Check if the current user is the owner of the job posting
    if candidate.job_posting.recruiter_id != current_user.id:
        flash('You do not have permission to view this candidate', 'danger')
        return redirect(url_for('dashboard'))
        
    return render_template('view_resume.html', candidate=candidate)

@app.route('/candidate/<int:candidate_id>/update_status', methods=['POST'])
@login_required
def update_candidate_status(candidate_id):
    """Update a candidate's status."""
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Check if the current user is the owner of the job posting
    if candidate.job_posting.recruiter_id != current_user.id:
        flash('You do not have permission to update this candidate', 'danger')
        return redirect(url_for('dashboard'))
        
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    if status:
        candidate.status = status
    
    if notes:
        candidate.notes = notes
        
    db.session.commit()
    
    flash('Candidate updated successfully!', 'success')
    return redirect(url_for('view_candidate', candidate_id=candidate_id))

@app.route('/download/<int:resume_id>')
@login_required
def download_resume(resume_id):
    """Download a resume file."""
    resume = Resume.query.get_or_404(resume_id)
    candidate = Candidate.query.get_or_404(resume.candidate_id)
    
    # Check if the current user is the owner of the job posting
    if candidate.job_posting.recruiter_id != current_user.id:
        flash('You do not have permission to download this resume', 'danger')
        return redirect(url_for('dashboard'))
        
    # Get directory and filename from file_path
    directory = os.path.dirname(resume.file_path)
    filename = os.path.basename(resume.file_path)
    
    return send_from_directory(directory, filename, as_attachment=True)

# Route for uploading resume page
@app.route('/upload_resume', methods=['GET', 'POST'])
@login_required
def upload_resume_page():
    """Generic resume upload page (not associated with a job)."""
    job_postings = JobPosting.query.filter_by(recruiter_id=current_user.id).all()
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['resume']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        job_id = request.form.get('job_id')
        
        if not job_id:
            flash('Please select a job posting', 'danger')
            return redirect(request.url)
            
        # Redirect to job-specific upload page
        return redirect(url_for('upload_resume', job_id=job_id))
        
    return render_template('upload_resume.html', job=None, job_postings=job_postings)
