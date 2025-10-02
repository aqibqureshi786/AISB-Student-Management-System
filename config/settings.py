"""
Configuration settings for the AISB Student Management System
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "config/firebase_credentials.json")

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# Admin Credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Application Settings
APP_NAME = os.getenv("APP_NAME", "AISB Student Management System")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Database Collections
STUDENTS_COLLECTION = "students"
QUIZZES_COLLECTION = "quizzes"
RESULTS_COLLECTION = "results"
ADMINS_COLLECTION = "admins"
