"""
Video submission utilities for Phase 2
"""
import streamlit as st
from database.firebase_manager import firebase_manager
from agents.video_analyzer import video_analyzer
from agents.email_agent import email_agent
from datetime import datetime
from typing import Dict, Any, Optional, List

class VideoSubmissionManager:
    def __init__(self):
        self.firebase_manager = firebase_manager
        self.video_analyzer = video_analyzer
        self.email_agent = email_agent
    
    def submit_video(self, student_id: str, student_email: str, video_link: str, topic: str = "General") -> Dict[str, Any]:
        """Handle video submission from student"""
        try:
            # Step 1: Validate the Google Drive link
            validation = self.video_analyzer.validate_google_drive_link(video_link)
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "message": validation["message"]
                }
            
            # Step 2: Check if student already submitted a video
            existing_video = self.firebase_manager.get_video_by_student(student_id)
            if existing_video:
                return {
                    "success": False,
                    "message": "You have already submitted a video. Only one submission is allowed per student."
                }
            
            # Step 3: Save video submission
            video_data = {
                "student_id": student_id,
                "video_link": video_link,
                "topic": topic,
                "submitted_at": datetime.now().isoformat(),
                "status": "submitted",
                "file_id": validation.get("file_id", ""),
                "direct_link": validation.get("direct_link", video_link)
            }
            
            video_id = self.firebase_manager.add_video_submission(video_data)
            
            if video_id:
                # Step 4: Send confirmation email
                self._send_video_submission_email(student_email, video_id)
                
                return {
                    "success": True,
                    "message": "Video submitted successfully! You will receive a confirmation email shortly.",
                    "video_id": video_id
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save video submission. Please try again."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error submitting video: {str(e)}"
            }
    
    def analyze_video(self, video_id: str) -> Dict[str, Any]:
        """Analyze a submitted video"""
        try:
            # Get video data
            videos = self.firebase_manager.get_all_videos()
            video_data = None
            
            for video in videos:
                if video.get('id') == video_id:
                    video_data = video
                    break
            
            if not video_data:
                return {
                    "success": False,
                    "message": "Video not found"
                }
            
            # Analyze the video
            analysis_result = self.video_analyzer.analyze_video_content(
                student_id=video_data.get('student_id', ''),
                video_link=video_data.get('video_link', ''),
                topic=video_data.get('topic', 'General')
            )
            
            if analysis_result["success"]:
                # Update video with analysis results
                analysis_data = {
                    "analysis_completed": True,
                    "analyzed_at": datetime.now().isoformat(),
                    "transcript": analysis_result.get("transcript", ""),
                    "video_score": analysis_result.get("score", 0),
                    "video_grade": analysis_result.get("grade", "F"),
                    "video_feedback": analysis_result.get("feedback", ""),
                    "detailed_analysis": analysis_result.get("detailed_analysis", {}),
                    "status": "analyzed"
                }
                
                self.firebase_manager.update_video_analysis(video_id, analysis_data)
                
                return {
                    "success": True,
                    "message": "Video analysis completed successfully",
                    "analysis": analysis_result
                }
            else:
                return analysis_result
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error analyzing video: {str(e)}"
            }
    
    def get_student_video_status(self, student_id: str) -> Dict[str, Any]:
        """Get video submission status for a student"""
        try:
            video = self.firebase_manager.get_video_by_student(student_id)
            
            if not video:
                return {
                    "submitted": False,
                    "message": "No video submission found"
                }
            
            return {
                "submitted": True,
                "video_id": video.get('id', ''),
                "submitted_at": video.get('submitted_at', ''),
                "status": video.get('status', 'submitted'),
                "analysis_completed": video.get('analysis_completed', False),
                "video_score": video.get('video_score', 0),
                "video_grade": video.get('video_grade', 'Pending'),
                "video_feedback": video.get('video_feedback', ''),
                "video_link": video.get('video_link', '')
            }
            
        except Exception as e:
            return {
                "submitted": False,
                "message": f"Error checking video status: {str(e)}"
            }
    
    def _send_video_submission_email(self, student_email: str, video_id: str):
        """Send video submission confirmation email"""
        try:
            subject = "Video Submission Confirmation - AISB Student Management System"
            content = f"""
            Dear Student,

            Your video submission has been received successfully!

            Submission Details:
            - Video ID: {video_id}
            - Submitted At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            - Status: Under Review

            Your video will be analyzed and graded shortly. You will receive another email once the analysis is complete.

            Thank you for your submission!

            Best regards,
            AISB Administration Team
            """
            
            # Send email using the email agent
            self.email_agent.send_email(
                recipient_email=student_email,
                subject=subject,
                content=content,
                email_type="video_submission_confirmation"
            )
            
        except Exception as e:
            print(f"❌ Error sending video submission email: {e}")

class FinalResultsManager:
    def __init__(self):
        self.firebase_manager = firebase_manager
        self.email_agent = email_agent
    
    def calculate_combined_results(self) -> List[Dict[str, Any]]:
        """Calculate combined quiz and video results for all students"""
        try:
            # Get all quiz results
            quiz_results = self.firebase_manager.get_all_results()
            
            # Get all video results
            video_results = self.firebase_manager.get_all_videos()
            
            # Combine results by student
            combined_results = {}
            
            # Process quiz results
            for quiz_result in quiz_results:
                student_id = quiz_result.get('student_id', '')
                if student_id:
                    combined_results[student_id] = {
                        "student_id": student_id,
                        "quiz_score": quiz_result.get('score_percentage', 0),
                        "quiz_grade": quiz_result.get('grade', 'F'),
                        "quiz_feedback": quiz_result.get('feedback', ''),
                        "quiz_submitted": True,
                        "video_score": 0,
                        "video_grade": 'Not Submitted',
                        "video_feedback": 'No video submission',
                        "video_submitted": False,
                        "total_score": 0,
                        "final_grade": 'Incomplete'
                    }
            
            # Process video results
            for video_result in video_results:
                student_id = video_result.get('student_id', '')
                if student_id in combined_results:
                    combined_results[student_id].update({
                        "video_score": video_result.get('video_score', 0),
                        "video_grade": video_result.get('video_grade', 'Pending'),
                        "video_feedback": video_result.get('video_feedback', ''),
                        "video_submitted": True,
                        "video_link": video_result.get('video_link', '')
                    })
            
            # Calculate total scores and final grades
            for student_id, result in combined_results.items():
                quiz_weight = 0.6  # 60% for quiz
                video_weight = 0.4  # 40% for video
                
                if result["video_submitted"]:
                    total_score = (result["quiz_score"] * quiz_weight) + (result["video_score"] * video_weight)
                else:
                    total_score = result["quiz_score"] * quiz_weight  # Only quiz score if no video
                
                result["total_score"] = round(total_score, 2)
                result["final_grade"] = self._calculate_final_grade(total_score)
            
            return list(combined_results.values())
            
        except Exception as e:
            print(f"❌ Error calculating combined results: {e}")
            return []
    
    def select_top_students(self, percentage: float) -> List[Dict[str, Any]]:
        """Select top students based on percentage"""
        try:
            combined_results = self.calculate_combined_results()
            
            # Sort by total score (descending)
            sorted_results = sorted(combined_results, key=lambda x: x["total_score"], reverse=True)
            
            # Calculate number of students to select
            total_students = len(sorted_results)
            num_to_select = max(1, int(total_students * (percentage / 100)))
            
            # Select top students
            top_students = sorted_results[:num_to_select]
            
            return top_students
            
        except Exception as e:
            print(f"❌ Error selecting top students: {e}")
            return []
    
    def release_final_results(self, selected_students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Release final results to selected students"""
        try:
            success_count = 0
            error_count = 0
            
            for student_result in selected_students:
                try:
                    # Save final result to database
                    final_result_data = {
                        "student_id": student_result["student_id"],
                        "quiz_score": student_result["quiz_score"],
                        "video_score": student_result["video_score"],
                        "total_score": student_result["total_score"],
                        "final_grade": student_result["final_grade"],
                        "selected": True,
                        "released_at": datetime.now().isoformat(),
                        "status": "selected"
                    }
                    
                    final_result_id = self.firebase_manager.add_final_result(final_result_data)
                    
                    if final_result_id:
                        # Send selection email
                        self._send_final_selection_email(student_result)
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"❌ Error processing student {student_result.get('student_id', 'Unknown')}: {e}")
                    error_count += 1
            
            return {
                "success": True,
                "message": f"Final results released successfully! {success_count} students notified, {error_count} errors.",
                "success_count": success_count,
                "error_count": error_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error releasing final results: {str(e)}"
            }
    
    def _calculate_final_grade(self, score: float) -> str:
        """Calculate final letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _send_final_selection_email(self, student_result: Dict[str, Any]):
        """Send final selection email to student"""
        try:
            # Get student email (you'll need to implement this)
            student_id = student_result["student_id"]
            
            # For now, use a placeholder email
            student_email = f"student_{student_id}@example.com"
            
            subject = "🎉 Congratulations! You've been selected - AISB Program"
            content = f"""
            Dear Student,

            Congratulations! We are pleased to inform you that you have been selected for the AISB program based on your outstanding performance.

            Your Final Results:
            - Quiz Score: {student_result['quiz_score']}%
            - Video Assessment Score: {student_result['video_score']}%
            - Total Score: {student_result['total_score']}%
            - Final Grade: {student_result['final_grade']}

            You have demonstrated excellent knowledge and presentation skills. We look forward to having you in our program!

            Next Steps:
            - You will receive further instructions via email within the next 48 hours
            - Please keep this email for your records

            Once again, congratulations on your achievement!

            Best regards,
            AISB Selection Committee
            """
            
            # Send email using the email agent
            self.email_agent.send_email(
                recipient_email=student_email,
                subject=subject,
                content=content,
                email_type="final_selection"
            )
            
        except Exception as e:
            print(f"❌ Error sending final selection email: {e}")

# Global instances
video_submission_manager = VideoSubmissionManager()
final_results_manager = FinalResultsManager()
