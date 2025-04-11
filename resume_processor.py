import os
import re
import logging
import docx2txt
import PyPDF2
from io import BytesIO
import spacy
import string

# Try to load spaCy model - use small model for efficiency
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # If model not installed, let's get very basic functionality working without it
    nlp = None
    logging.warning("spaCy model not found. Basic text processing will be used instead.")

# Define common skills for matching (could be expanded or loaded from a file)
COMMON_SKILLS = [
    # Programming Languages
    'python', 'java', 'javascript', 'js', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
    # Web Development
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
    # Data Science
    'machine learning', 'data analysis', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scipy',
    'scikit-learn', 'r', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'data visualization',
    # DevOps & Cloud
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
    # Soft Skills
    'project management', 'agile', 'scrum', 'communication', 'problem solving', 'teamwork',
    'leadership', 'time management'
]

class ResumeProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_file):
        """Extract text from a PDF file."""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {str(e)}")
            return ""

    @staticmethod
    def extract_text_from_docx(docx_file):
        """Extract text from a DOCX file."""
        try:
            text = docx2txt.process(docx_file)
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from DOCX: {str(e)}")
            return ""

    @staticmethod
    def extract_text(file):
        """Extract text from a resume file based on its extension."""
        filename = file.filename.lower()
        file.seek(0)  # Ensure we're at the beginning of the file
        
        if filename.endswith('.pdf'):
            return ResumeProcessor.extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            return ResumeProcessor.extract_text_from_docx(file)
        else:
            return ""

    @staticmethod
    def extract_skills(text):
        """Extract skills from resume text."""
        skills = []
        
        # Simple skill extraction using the skills list
        text_lower = text.lower()
        
        # Remove punctuation and extra spaces
        translator = str.maketrans('', '', string.punctuation)
        text_lower = text_lower.translate(translator)
        
        for skill in COMMON_SKILLS:
            # Match full words only, not partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills.append(skill)
        
        # If spaCy is available, enhance skill extraction
        if nlp:
            doc = nlp(text)
            # Extract noun phrases as potential skills
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower()
                # Check if the noun phrase contains known skills
                for skill in COMMON_SKILLS:
                    if skill in chunk_text and skill not in skills:
                        skills.append(skill)

        return skills

    @staticmethod
    def extract_education(text):
        """Extract education information from resume text."""
        education_keywords = ['education', 'degree', 'university', 'college', 'school', 'bachelor', 'master', 'phd', 'diploma']
        education_text = ""
        
        lines = text.split('\n')
        in_education_section = False
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if this line indicates the start of an education section
            if any(keyword in line_lower for keyword in education_keywords):
                in_education_section = True
                education_text += line + "\n"
            # If we're in an education section, add lines until we hit another section
            elif in_education_section:
                # Check if this line might indicate the start of a new section
                if line.strip() and line.strip()[0].isupper() and any(char.isdigit() for char in line):
                    # Likely a date or a new section header
                    in_education_section = False
                else:
                    education_text += line + "\n"
        
        # If no structured education section found, use regex to extract education-related lines
        if not education_text:
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in education_keywords):
                    education_text += line + "\n"
        
        return education_text.strip()

    @staticmethod
    def extract_experience(text):
        """Extract work experience information from resume text."""
        experience_keywords = ['experience', 'work', 'employment', 'job', 'career', 'professional']
        experience_text = ""
        
        lines = text.split('\n')
        in_experience_section = False
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if this line indicates the start of an experience section
            if any(keyword in line_lower for keyword in experience_keywords) and not "education" in line_lower:
                in_experience_section = True
                experience_text += line + "\n"
            # If we're in an experience section, add lines until we hit another section
            elif in_experience_section:
                # Check if this line might indicate the start of a new section
                if line.strip() and line.strip()[0].isupper() and "education" in line.lower():
                    # New section header
                    in_experience_section = False
                else:
                    experience_text += line + "\n"
        
        # If no structured experience section found, use regex to extract experience-related lines
        if not experience_text:
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in experience_keywords) and not "education" in line_lower:
                    experience_text += line + "\n"
        
        return experience_text.strip()

    @staticmethod
    def calculate_match_score(resume_text, job_requirements):
        """Calculate match score between resume and job requirements."""
        if not resume_text or not job_requirements:
            return 0.0
            
        # Extract skills from resume
        resume_skills = ResumeProcessor.extract_skills(resume_text)
        
        # Extract skills from job requirements
        requirements_skills = ResumeProcessor.extract_skills(job_requirements)
        
        if not requirements_skills:
            return 0.0
            
        # Calculate match score based on matching skills
        matching_skills = [skill for skill in resume_skills if skill in requirements_skills]
        
        # Calculate score as a percentage
        score = (len(matching_skills) / len(requirements_skills)) * 100
        
        return min(score, 100.0)  # Cap at 100%

    @staticmethod
    def process_resume(file, job_requirements=None):
        """Process a resume file and extract relevant information."""
        try:
            # Reset file pointer
            file.seek(0)
            
            # Extract text from resume
            text = ResumeProcessor.extract_text(file)
            
            if not text:
                return {
                    'success': False,
                    'error': 'Could not extract text from file.'
                }
                
            # Extract information
            skills = ResumeProcessor.extract_skills(text)
            education = ResumeProcessor.extract_education(text)
            experience = ResumeProcessor.extract_experience(text)
            
            # Reset file pointer again for any further processing
            file.seek(0)
            
            # Calculate match score if job requirements provided
            match_score = 0.0
            if job_requirements:
                match_score = ResumeProcessor.calculate_match_score(text, job_requirements)
                
            return {
                'success': True,
                'text': text,
                'skills': skills,
                'skills_text': ', '.join(skills),
                'education': education,
                'experience': experience,
                'match_score': match_score
            }
            
        except Exception as e:
            logging.error(f"Error processing resume: {str(e)}")
            return {
                'success': False,
                'error': f'Error processing resume: {str(e)}'
            }
