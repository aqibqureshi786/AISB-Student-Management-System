"""
Authentication utilities for AISB Student Management System
"""
import bcrypt
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any
from database.firebase_manager import firebase_manager
from config.settings import ADMIN_USERNAME, ADMIN_PASSWORD

class AuthManager:
    def __init__(self):
        self.firebase_manager = firebase_manager
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def register_student(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new student"""
        try:
            # Check if student already exists
            existing_student = self.firebase_manager.get_student_by_email(email)
            if existing_student:
                return {"success": False, "message": "Student with this email already exists"}
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create student data
            student_data = {
                "name": name,
                "email": email,
                "password": hashed_password,
                "registration_date": str(pd.Timestamp.now()),
                "status": "active"
            }
            
            # Add to database
            student_id = self.firebase_manager.add_student(student_data)
            
            if student_id:
                return {
                    "success": True, 
                    "message": "Registration successful",
                    "student_id": student_id
                }
            else:
                return {"success": False, "message": "Failed to register student"}
                
        except Exception as e:
            return {"success": False, "message": f"Registration error: {str(e)}"}
    
    def login_student(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate student login"""
        try:
            student = self.firebase_manager.get_student_by_email(email)
            
            if not student:
                return {"success": False, "message": "Student not found"}
            
            if self.verify_password(password, student.get("password", "")):
                return {
                    "success": True,
                    "message": "Login successful",
                    "student": {
                        "id": student.get("id"),
                        "name": student.get("name"),
                        "email": student.get("email")
                    }
                }
            else:
                return {"success": False, "message": "Invalid password"}
                
        except Exception as e:
            return {"success": False, "message": f"Login error: {str(e)}"}
    
    def login_admin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate admin login"""
        try:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                return {
                    "success": True,
                    "message": "Admin login successful",
                    "admin": {
                        "username": username,
                        "role": "admin"
                    }
                }
            else:
                return {"success": False, "message": "Invalid admin credentials"}
                
        except Exception as e:
            return {"success": False, "message": f"Admin login error: {str(e)}"}
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return "user" in st.session_state or "admin" in st.session_state
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current logged in user"""
        if "user" in st.session_state:
            return st.session_state.user
        elif "admin" in st.session_state:
            return st.session_state.admin
        return None
    
    def logout(self):
        """Logout current user"""
        if "user" in st.session_state:
            del st.session_state.user
        if "admin" in st.session_state:
            del st.session_state.admin
        st.rerun()

# Global instance
auth_manager = AuthManager()
