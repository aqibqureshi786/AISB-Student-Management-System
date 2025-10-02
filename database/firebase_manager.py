"""
Firebase Database Manager for AISB Student Management System
"""
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Optional, Any
import json
from config.settings import FIREBASE_CREDENTIALS_PATH, STUDENTS_COLLECTION, QUIZZES_COLLECTION, RESULTS_COLLECTION

class FirebaseManager:
    def __init__(self):
        self.db = None
        self.use_local_storage = False
        self.local_storage = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            if not firebase_admin._apps:
                # Initialize Firebase with credentials
                cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            print("Firebase initialized successfully!")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            print("🔄 Falling back to local JSON storage...")
            self.use_local_storage = True
            from database.local_storage import local_storage_manager
            self.local_storage = local_storage_manager
            print("✅ Local storage initialized successfully!")
    
    def add_student(self, student_data: Dict[str, Any]) -> str:
        """Add a new student to the database"""
        try:
            if self.use_local_storage:
                return self.local_storage.add_student(student_data)
            elif self.db:
                doc_ref = self.db.collection(STUDENTS_COLLECTION).add(student_data)
                return doc_ref[1].id
            else:
                # Mock implementation for development
                return "mock_student_id"
        except Exception as e:
            print(f"Error adding student: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for student registration...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.add_student(student_data)
            return ""
    
    def get_student_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get student by email"""
        try:
            if self.use_local_storage:
                return self.local_storage.get_student_by_email(email)
            elif self.db:
                students = self.db.collection(STUDENTS_COLLECTION).where("email", "==", email).get()
                if students:
                    student_doc = students[0]
                    student_data = student_doc.to_dict()
                    student_data['id'] = student_doc.id
                    return student_data
                return None
            else:
                # Mock implementation
                return {"id": "mock_id", "email": email, "name": "Mock Student"}
        except Exception as e:
            print(f"Error getting student: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for student lookup...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.get_student_by_email(email)
            return None
    
    def add_quiz(self, quiz_data: Dict[str, Any]) -> str:
        """Add a new quiz to the database"""
        try:
            if self.use_local_storage:
                return self.local_storage.add_quiz(quiz_data)
            elif self.db:
                doc_ref = self.db.collection(QUIZZES_COLLECTION).add(quiz_data)
                return doc_ref[1].id
            else:
                return "mock_quiz_id"
        except Exception as e:
            print(f"Error adding quiz: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage due to Firestore API issue...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.add_quiz(quiz_data)
            return ""
    
    def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Get quiz by ID"""
        try:
            if self.db:
                doc = self.db.collection(QUIZZES_COLLECTION).document(quiz_id).get()
                if doc.exists:
                    quiz_data = doc.to_dict()
                    quiz_data['id'] = doc.id
                    return quiz_data
                return None
            else:
                return {"id": quiz_id, "topic": "Mock Topic", "questions": []}
        except Exception as e:
            print(f"Error getting quiz: {e}")
            return None
    
    def get_all_quizzes(self) -> List[Dict[str, Any]]:
        """Get all quizzes"""
        try:
            if self.use_local_storage:
                return self.local_storage.get_all_quizzes()
            elif self.db:
                quizzes = []
                docs = self.db.collection(QUIZZES_COLLECTION).get()
                for doc in docs:
                    quiz_data = doc.to_dict()
                    quiz_data['id'] = doc.id
                    quizzes.append(quiz_data)
                return quizzes
            else:
                return [{"id": "mock_quiz_1", "topic": "AI Basics", "questions": []}]
        except Exception as e:
            print(f"Error getting quizzes: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for quiz retrieval...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.get_all_quizzes()
            return []
    
    def add_result(self, result_data: Dict[str, Any]) -> str:
        """Add quiz result to database"""
        try:
            if self.use_local_storage:
                return self.local_storage.add_result(result_data)
            elif self.db:
                doc_ref = self.db.collection(RESULTS_COLLECTION).add(result_data)
                return doc_ref[1].id
            else:
                return "mock_result_id"
        except Exception as e:
            print(f"Error adding result: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for result storage...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.add_result(result_data)
            return ""
    
    def get_results_by_quiz(self, quiz_id: str) -> List[Dict[str, Any]]:
        """Get all results for a specific quiz"""
        try:
            if self.use_local_storage:
                return self.local_storage.get_results_by_quiz(quiz_id)
            elif self.db:
                results = []
                docs = self.db.collection(RESULTS_COLLECTION).where("quiz_id", "==", quiz_id).get()
                for doc in docs:
                    result_data = doc.to_dict()
                    result_data['id'] = doc.id
                    results.append(result_data)
                return results
            else:
                return [{"id": "mock_result", "quiz_id": quiz_id, "student_id": "mock_student", "score": 85}]
        except Exception as e:
            print(f"Error getting results: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for results retrieval...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.get_results_by_quiz(quiz_id)
            return []
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all quiz results"""
        try:
            if self.use_local_storage:
                return self.local_storage.get_all_results()
            elif self.db:
                results = []
                docs = self.db.collection(RESULTS_COLLECTION).get()
                for doc in docs:
                    result_data = doc.to_dict()
                    result_data['id'] = doc.id
                    results.append(result_data)
                return results
            else:
                return [{"id": "mock_result", "student_id": "mock_student", "score_percentage": 85}]
        except Exception as e:
            print(f"Error getting all results: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for all results...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.get_all_results()
            return []
    
    def get_student_results(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all results for a specific student"""
        try:
            if self.use_local_storage:
                return self.local_storage.get_student_results(student_id)
            elif self.db:
                results = []
                docs = self.db.collection(RESULTS_COLLECTION).where("student_id", "==", student_id).get()
                for doc in docs:
                    result_data = doc.to_dict()
                    result_data['id'] = doc.id
                    results.append(result_data)
                return results
            else:
                return [{"id": "mock_result", "quiz_id": "mock_quiz", "student_id": student_id, "score": 85}]
        except Exception as e:
            print(f"Error getting student results: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for student results...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.get_student_results(student_id)
            return []
    
    def update_result_status(self, result_id: str, status: str) -> bool:
        """Update result release status"""
        try:
            if self.use_local_storage:
                return self.local_storage.update_result_status(result_id, status)
            elif self.db:
                self.db.collection(RESULTS_COLLECTION).document(result_id).update({"status": status})
                return True
            else:
                return True
        except Exception as e:
            print(f"Error updating result status: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for result status update...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.update_result_status(result_id, status)
            return False
    
    def add_video_submission(self, video_data: Dict[str, Any]) -> str:
        """Add video submission to database"""
        try:
            if self.use_local_storage:
                return self.local_storage.add_video_submission(video_data)
            elif self.db:
                doc_ref = self.db.collection("videos").add(video_data)
                return doc_ref[1].id
            else:
                return "mock_video_id"
        except Exception as e:
            print(f"Error adding video submission: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for video submission...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.add_video_submission(video_data)
            return ""
    
    def get_video_by_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get video submission by student ID"""
        try:
            if self.use_local_storage:
                return self.local_storage.get_video_by_student(student_id)
            elif self.db:
                docs = self.db.collection("videos").where("student_id", "==", student_id).get()
                for doc in docs:
                    video_data = doc.to_dict()
                    video_data['id'] = doc.id
                    return video_data
                return None
            else:
                return {"id": "mock_video", "student_id": student_id, "video_link": "mock_link"}
        except Exception as e:
            print(f"Error getting video: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for video retrieval...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.get_video_by_student(student_id)
            return None
    
    def get_all_videos(self) -> List[Dict[str, Any]]:
        """Get all video submissions"""
        try:
            if self.use_local_storage:
                return self.local_storage.get_all_videos()
            elif self.db:
                videos = []
                docs = self.db.collection("videos").get()
                for doc in docs:
                    video_data = doc.to_dict()
                    video_data['id'] = doc.id
                    videos.append(video_data)
                return videos
            else:
                return [{"id": "mock_video", "student_id": "mock_student", "video_link": "mock_link"}]
        except Exception as e:
            print(f"Error getting videos: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for video retrieval...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.get_all_videos()
            return []
    
    def update_video_analysis(self, video_id: str, analysis_data: Dict[str, Any]) -> bool:
        """Update video with analysis results"""
        try:
            if self.use_local_storage:
                return self.local_storage.update_video_analysis(video_id, analysis_data)
            elif self.db:
                self.db.collection("videos").document(video_id).update(analysis_data)
                return True
            else:
                return True
        except Exception as e:
            print(f"Error updating video analysis: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for video analysis update...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.update_video_analysis(video_id, analysis_data)
            return False
    
    def add_final_result(self, final_result_data: Dict[str, Any]) -> str:
        """Add final combined result"""
        try:
            if self.use_local_storage:
                return self.local_storage.add_final_result(final_result_data)
            elif self.db:
                doc_ref = self.db.collection("final_results").add(final_result_data)
                return doc_ref[1].id
            else:
                return "mock_final_result_id"
        except Exception as e:
            print(f"Error adding final result: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for final result...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.add_final_result(final_result_data)
            return ""
    
    def get_final_results(self) -> List[Dict[str, Any]]:
        """Get all final results"""
        try:
            if self.use_local_storage:
                return self.local_storage.get_final_results()
            elif self.db:
                results = []
                docs = self.db.collection("final_results").get()
                for doc in docs:
                    result_data = doc.to_dict()
                    result_data['id'] = doc.id
                    results.append(result_data)
                return results
            else:
                return [{"id": "mock_final", "student_id": "mock_student", "total_score": 85}]
        except Exception as e:
            print(f"Error getting final results: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for final results...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.get_final_results()
            return []
    
    def get_student_final_result(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get final result for a specific student"""
        try:
            if self.use_local_storage:
                return self.local_storage.get_student_final_result(student_id)
            elif self.db:
                docs = self.db.collection("final_results").where("student_id", "==", student_id).get()
                for doc in docs:
                    result_data = doc.to_dict()
                    result_data['id'] = doc.id
                    return result_data
                return None
            else:
                return {"id": "mock_final", "student_id": student_id, "total_score": 85}
        except Exception as e:
            print(f"Error getting student final result: {e}")
            # If Firestore API is disabled, switch to local storage
            if "SERVICE_DISABLED" in str(e) or "Cloud Firestore API" in str(e):
                print("🔄 Switching to local storage for student final result...")
                self.use_local_storage = True
                if not self.local_storage:
                    from database.local_storage import local_storage_manager
                    self.local_storage = local_storage_manager
                return self.local_storage.get_student_final_result(student_id)
            return None

# Global instance
firebase_manager = FirebaseManager()
