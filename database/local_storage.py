"""
Local JSON Storage Manager for AISB Student Management System
(Alternative to Firebase when API is not enabled)
"""
import json
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

class LocalStorageManager:
    def __init__(self):
        self.data_dir = "local_data"
        self.students_file = os.path.join(self.data_dir, "students.json")
        self.quizzes_file = os.path.join(self.data_dir, "quizzes.json")
        self.results_file = os.path.join(self.data_dir, "results.json")
        self.videos_file = os.path.join(self.data_dir, "videos.json")
        self.final_results_file = os.path.join(self.data_dir, "final_results.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize JSON files if they don't exist"""
        for file_path in [self.students_file, self.quizzes_file, self.results_file, 
                         self.videos_file, self.final_results_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
    def _load_data(self, file_path: str) -> Dict:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, file_path: str, data: Dict):
        """Save data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_student(self, student_data: Dict[str, Any]) -> str:
        """Add a new student"""
        try:
            students = self._load_data(self.students_file)
            student_id = str(uuid.uuid4())
            student_data['id'] = student_id
            students[student_id] = student_data
            self._save_data(self.students_file, students)
            print(f"✅ Student added with ID: {student_id}")
            return student_id
        except Exception as e:
            print(f"❌ Error adding student: {e}")
            return ""
    
    def get_student_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get student by email"""
        try:
            students = self._load_data(self.students_file)
            for student_id, student_data in students.items():
                if student_data.get('email') == email:
                    student_data['id'] = student_id
                    return student_data
            return None
        except Exception as e:
            print(f"❌ Error getting student: {e}")
            return None
    
    def add_quiz(self, quiz_data: Dict[str, Any]) -> str:
        """Add a new quiz"""
        try:
            quizzes = self._load_data(self.quizzes_file)
            quiz_id = str(uuid.uuid4())
            quiz_data['id'] = quiz_id
            quizzes[quiz_id] = quiz_data
            self._save_data(self.quizzes_file, quizzes)
            print(f"✅ Quiz saved with ID: {quiz_id}")
            return quiz_id
        except Exception as e:
            print(f"❌ Error adding quiz: {e}")
            return ""
    
    def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Get quiz by ID"""
        try:
            quizzes = self._load_data(self.quizzes_file)
            quiz_data = quizzes.get(quiz_id)
            if quiz_data:
                quiz_data['id'] = quiz_id
            return quiz_data
        except Exception as e:
            print(f"❌ Error getting quiz: {e}")
            return None
    
    def get_all_quizzes(self) -> List[Dict[str, Any]]:
        """Get all quizzes"""
        try:
            quizzes = self._load_data(self.quizzes_file)
            quiz_list = []
            for quiz_id, quiz_data in quizzes.items():
                quiz_data['id'] = quiz_id
                quiz_list.append(quiz_data)
            return quiz_list
        except Exception as e:
            print(f"❌ Error getting quizzes: {e}")
            return []
    
    def add_result(self, result_data: Dict[str, Any]) -> str:
        """Add quiz result"""
        try:
            results = self._load_data(self.results_file)
            result_id = str(uuid.uuid4())
            result_data['id'] = result_id
            results[result_id] = result_data
            self._save_data(self.results_file, results)
            print(f"✅ Result saved with ID: {result_id}")
            return result_id
        except Exception as e:
            print(f"❌ Error adding result: {e}")
            return ""
    
    def get_results_by_quiz(self, quiz_id: str) -> List[Dict[str, Any]]:
        """Get all results for a specific quiz"""
        try:
            results = self._load_data(self.results_file)
            quiz_results = []
            for result_id, result_data in results.items():
                if result_data.get('quiz_id') == quiz_id:
                    result_data['id'] = result_id
                    quiz_results.append(result_data)
            return quiz_results
        except Exception as e:
            print(f"❌ Error getting results: {e}")
            return []
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all quiz results"""
        try:
            results = self._load_data(self.results_file)
            results_list = []
            for result_id, result_data in results.items():
                result_data['id'] = result_id
                results_list.append(result_data)
            return results_list
        except Exception as e:
            print(f"❌ Error getting all results: {e}")
            return []
    
    def get_student_results(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all results for a specific student"""
        try:
            results = self._load_data(self.results_file)
            student_results = []
            for result_id, result_data in results.items():
                if result_data.get('student_id') == student_id:
                    result_data['id'] = result_id
                    student_results.append(result_data)
            return student_results
        except Exception as e:
            print(f"❌ Error getting student results: {e}")
            return []
    
    def update_result_status(self, result_id: str, status: str) -> bool:
        """Update result release status"""
        try:
            results = self._load_data(self.results_file)
            if result_id in results:
                results[result_id]['status'] = status
                self._save_data(self.results_file, results)
                print(f"✅ Result {result_id} status updated to {status}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error updating result status: {e}")
            return False
    
    def add_video_submission(self, video_data: Dict[str, Any]) -> str:
        """Add video submission"""
        try:
            videos = self._load_data(self.videos_file)
            video_id = str(uuid.uuid4())
            video_data['id'] = video_id
            videos[video_id] = video_data
            self._save_data(self.videos_file, videos)
            print(f"✅ Video submission saved with ID: {video_id}")
            return video_id
        except Exception as e:
            print(f"❌ Error adding video submission: {e}")
            return ""
    
    def get_video_by_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get video submission by student ID"""
        try:
            videos = self._load_data(self.videos_file)
            for video_id, video_data in videos.items():
                if video_data.get('student_id') == student_id:
                    video_data['id'] = video_id
                    return video_data
            return None
        except Exception as e:
            print(f"❌ Error getting video: {e}")
            return None
    
    def get_all_videos(self) -> List[Dict[str, Any]]:
        """Get all video submissions"""
        try:
            videos = self._load_data(self.videos_file)
            video_list = []
            for video_id, video_data in videos.items():
                video_data['id'] = video_id
                video_list.append(video_data)
            return video_list
        except Exception as e:
            print(f"❌ Error getting videos: {e}")
            return []
    
    def update_video_analysis(self, video_id: str, analysis_data: Dict[str, Any]) -> bool:
        """Update video with analysis results"""
        try:
            videos = self._load_data(self.videos_file)
            if video_id in videos:
                videos[video_id].update(analysis_data)
                self._save_data(self.videos_file, videos)
                print(f"✅ Video analysis updated for ID: {video_id}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error updating video analysis: {e}")
            return False
    
    def add_final_result(self, final_result_data: Dict[str, Any]) -> str:
        """Add final combined result"""
        try:
            final_results = self._load_data(self.final_results_file)
            result_id = str(uuid.uuid4())
            final_result_data['id'] = result_id
            final_results[result_id] = final_result_data
            self._save_data(self.final_results_file, final_results)
            print(f"✅ Final result saved with ID: {result_id}")
            return result_id
        except Exception as e:
            print(f"❌ Error adding final result: {e}")
            return ""
    
    def get_final_results(self) -> List[Dict[str, Any]]:
        """Get all final results"""
        try:
            final_results = self._load_data(self.final_results_file)
            results_list = []
            for result_id, result_data in final_results.items():
                result_data['id'] = result_id
                results_list.append(result_data)
            return results_list
        except Exception as e:
            print(f"❌ Error getting final results: {e}")
            return []
    
    def get_student_final_result(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get final result for a specific student"""
        try:
            final_results = self._load_data(self.final_results_file)
            for result_id, result_data in final_results.items():
                if result_data.get('student_id') == student_id:
                    result_data['id'] = result_id
                    return result_data
            return None
        except Exception as e:
            print(f"❌ Error getting student final result: {e}")
            return None

# Global instance
local_storage_manager = LocalStorageManager()
