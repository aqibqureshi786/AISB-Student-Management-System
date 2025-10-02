"""
Student Terminal for AISB Student Management System
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

from utils.auth import auth_manager
from database.firebase_manager import firebase_manager
from agents.quiz_grader import quiz_grader
from agents.email_agent import email_agent
from utils.video_utils import video_submission_manager, final_results_manager

class StudentTerminal:
    def __init__(self):
        self.auth_manager = auth_manager
        self.firebase_manager = firebase_manager
        self.quiz_grader = quiz_grader
        self.email_agent = email_agent
    
    def run(self):
        """Main student terminal interface"""
        st.set_page_config(
            page_title="AISB Student Portal",
            page_icon="🎓",
            layout="wide"
        )
        
        st.title("🎓 AISB Student Portal")
        st.markdown("---")
        
        # Check if student is logged in
        if "user" not in st.session_state:
            self.show_auth_interface()
        else:
            self.show_student_dashboard()
    
    def show_auth_interface(self):
        """Display login/registration interface"""
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            self.show_login()
        
        with tab2:
            self.show_registration()
    
    def show_login(self):
        """Display student login form"""
        st.subheader("🔐 Student Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("student_login"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Login")
                
                if submit_button:
                    if email and password:
                        result = self.auth_manager.login_student(email, password)
                        
                        if result["success"]:
                            st.session_state.user = result["student"]
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(result["message"])
                    else:
                        st.error("Please enter both email and password")
    
    def show_registration(self):
        """Display student registration form"""
        st.subheader("📝 Student Registration")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("student_registration"):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit_button = st.form_submit_button("Register")
                
                if submit_button:
                    if name and email and password and confirm_password:
                        if password != confirm_password:
                            st.error("Passwords do not match")
                        elif len(password) < 6:
                            st.error("Password must be at least 6 characters long")
                        else:
                            result = self.auth_manager.register_student(name, email, password)
                            
                            if result["success"]:
                                st.success("Registration successful! Please login.")
                                
                                # Send registration confirmation email
                                self.email_agent.send_registration_confirmation(email, name)
                            else:
                                st.error(result["message"])
                    else:
                        st.error("Please fill in all fields")
    
    def show_student_dashboard(self):
        """Display main student dashboard"""
        # Sidebar navigation
        st.sidebar.title("Navigation")
        student_name = st.session_state.user.get("name", "Student")
        st.sidebar.write(f"Welcome, {student_name}!")
        
        menu_options = [
            "Dashboard",
            "Available Quizzes",
            "Take Quiz",
            "My Results",
            "Video Assessment",
            "Final Results",
            "Profile"
        ]
        
        selected_option = st.sidebar.selectbox("Select Option", menu_options)
        
        if st.sidebar.button("Logout"):
            self.auth_manager.logout()
        
        # Main content based on selection
        if selected_option == "Dashboard":
            self.show_dashboard_overview()
        elif selected_option == "Available Quizzes":
            self.show_available_quizzes()
        elif selected_option == "Take Quiz":
            self.show_take_quiz()
        elif selected_option == "My Results":
            self.show_my_results()
        elif selected_option == "Video Assessment":
            self.show_video_assessment()
        elif selected_option == "Final Results":
            self.show_final_results()
        elif selected_option == "Profile":
            self.show_profile()
    
    def show_dashboard_overview(self):
        """Display student dashboard overview"""
        st.header("📊 Dashboard")
        
        student_id = st.session_state.user.get("id", "")
        
        # Get student statistics
        results = self.firebase_manager.get_student_results(student_id)
        quizzes = self.firebase_manager.get_all_quizzes()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Available Quizzes", len(quizzes))
        
        with col2:
            st.metric("Quizzes Taken", len(results))
        
        with col3:
            if results:
                avg_score = sum([r.get('score_percentage', 0) for r in results]) / len(results)
                st.metric("Average Score", f"{avg_score:.1f}%")
            else:
                st.metric("Average Score", "N/A")
        
        with col4:
            released_results = [r for r in results if r.get('status') == 'released']
            st.metric("Results Available", len(released_results))
        
        st.markdown("---")
        
        # Recent activity
        st.subheader("📋 Recent Activity")
        if results:
            recent_results = results[-3:]  # Show last 3 results
            for result in recent_results:
                quiz = self.firebase_manager.get_quiz(result.get('quiz_id', ''))
                quiz_topic = quiz.get('topic', 'Unknown Quiz') if quiz else 'Unknown Quiz'
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"📝 {quiz_topic}")
                
                with col2:
                    if result.get('status') == 'released':
                        st.write(f"Score: {result.get('score_percentage', 0):.1f}%")
                    else:
                        st.write("Pending")
                
                with col3:
                    st.write(result.get('submitted_at', 'Unknown'))
        else:
            st.info("No quiz activity yet. Take your first quiz!")
    
    def show_available_quizzes(self):
        """Display all available quizzes"""
        st.header("📚 Available Quizzes")
        
        quizzes = self.firebase_manager.get_all_quizzes()
        student_id = st.session_state.user.get("id", "")
        
        if quizzes:
            for quiz in quizzes:
                # Check if student has already taken this quiz
                results = self.firebase_manager.get_results_by_quiz(quiz.get('id', ''))
                student_result = next((r for r in results if r.get('student_id') == student_id), None)
                
                with st.expander(f"📝 {quiz.get('topic', 'Unknown Topic')} - {quiz.get('difficulty', 'Unknown')} Level"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Questions:** {quiz.get('total_questions', 0)}")
                        st.write(f"**Type:** {quiz.get('question_type', 'Unknown')}")
                        st.write(f"**Difficulty:** {quiz.get('difficulty', 'Unknown')}")
                    
                    with col2:
                        if student_result:
                            st.write("**Status:** ✅ Completed")
                            if student_result.get('status') == 'released':
                                st.write(f"**Your Score:** {student_result.get('score_percentage', 0):.1f}%")
                            else:
                                st.write("**Your Score:** Pending")
                        else:
                            st.write("**Status:** ⏳ Not taken")
                    
                    if quiz.get('description'):
                        st.write(f"**Description:** {quiz.get('description')}")
                    
                    if not student_result:
                        if st.button(f"Take Quiz", key=f"take_{quiz.get('id', '')}", type="primary"):
                            st.session_state.selected_quiz = quiz
                            st.session_state.page = "take_quiz"
                            st.rerun()
                    else:
                        st.info("You have already taken this quiz.")
        else:
            st.info("No quizzes available at the moment.")
    
    def show_take_quiz(self):
        """Interface for taking a quiz"""
        if "selected_quiz" not in st.session_state:
            st.header("📝 Take Quiz")
            st.info("Please select a quiz from the Available Quizzes section.")
            return
        
        quiz = st.session_state.selected_quiz
        st.header(f"📝 {quiz.get('topic', 'Quiz')}")
        
        st.write(f"**Difficulty:** {quiz.get('difficulty', 'Unknown')}")
        st.write(f"**Questions:** {quiz.get('total_questions', 0)}")
        st.write(f"**Type:** {quiz.get('question_type', 'Unknown')}")
        
        if quiz.get('description'):
            st.write(f"**Description:** {quiz.get('description')}")
        
        st.markdown("---")
        
        questions = quiz.get('questions', [])
        
        if not questions:
            st.error("No questions found in this quiz.")
            return
        
        # Quiz form
        with st.form("quiz_submission"):
            answers = []
            
            for i, question in enumerate(questions):
                st.subheader(f"Question {i + 1}")
                st.write(question.get('question', 'No question'))
                
                question_type = quiz.get('question_type', 'MCQ')
                
                if question_type == "MCQ":
                    options = question.get('options', [])
                    if options:
                        # Extract just the option text (remove A), B), etc.)
                        clean_options = [opt.split(') ', 1)[1] if ') ' in opt else opt for opt in options]
                        selected = st.radio(
                            "Select your answer:",
                            clean_options,
                            key=f"q_{i}",
                            index=None
                        )
                        
                        # Convert back to original format for grading
                        if selected:
                            for j, opt in enumerate(clean_options):
                                if opt == selected:
                                    answer_letter = chr(65 + j)  # A, B, C, D
                                    answers.append(answer_letter)
                                    break
                        else:
                            answers.append("")
                    else:
                        answers.append("")
                
                elif question_type == "True/False":
                    selected = st.radio(
                        "Select your answer:",
                        ["True", "False"],
                        key=f"q_{i}",
                        index=None
                    )
                    answers.append(selected if selected else "")
                
                else:  # Q/A
                    answer = st.text_area(
                        "Your answer:",
                        key=f"q_{i}",
                        height=100
                    )
                    answers.append(answer)
                
                st.markdown("---")
            
            submit_button = st.form_submit_button("Submit Quiz", type="primary")
            
            if submit_button:
                # Check if all questions are answered
                unanswered = [i + 1 for i, ans in enumerate(answers) if not ans.strip()]
                
                if unanswered:
                    st.error(f"Please answer all questions. Unanswered: {', '.join(map(str, unanswered))}")
                else:
                    with st.spinner("Submitting your quiz..."):
                        # Grade the quiz
                        correct_answers = [q.get('correct_answer', '') for q in questions]
                        grading_result = self.quiz_grader.grade_quiz(
                            student_answers=answers,
                            correct_answers=correct_answers,
                            questions=questions,
                            question_type=quiz.get('question_type', 'MCQ')
                        )
                        
                        # Save result to database
                        result_data = {
                            "student_id": st.session_state.user.get("id", ""),
                            "quiz_id": quiz.get("id", ""),
                            "answers": answers,
                            "score_percentage": grading_result.get("score_percentage", 0),
                            "grade": grading_result.get("grade", "F"),
                            "feedback": grading_result.get("overall_feedback", ""),
                            "question_results": grading_result.get("question_results", []),
                            "submitted_at": datetime.now().isoformat(),
                            "status": "pending"  # Admin needs to release results
                        }
                        
                        result_id = self.firebase_manager.add_result(result_data)
                        
                        if result_id:
                            st.success("Quiz submitted successfully!")
                            
                            # Send confirmation email
                            student_email = st.session_state.user.get("email", "")
                            student_name = st.session_state.user.get("name", "")
                            self.email_agent.send_quiz_submission_confirmation(
                                student_email, student_name, quiz.get('topic', 'Quiz'),
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            )
                            
                            # Clear selected quiz
                            if "selected_quiz" in st.session_state:
                                del st.session_state.selected_quiz
                            
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Failed to submit quiz. Please try again.")
    
    def show_my_results(self):
        """Display student's quiz results"""
        st.header("📊 My Results")
        
        student_id = st.session_state.user.get("id", "")
        results = self.firebase_manager.get_student_results(student_id)
        
        if results:
            for result in results:
                quiz = self.firebase_manager.get_quiz(result.get('quiz_id', ''))
                quiz_topic = quiz.get('topic', 'Unknown Quiz') if quiz else 'Unknown Quiz'
                
                with st.expander(f"📝 {quiz_topic} - {result.get('submitted_at', 'Unknown Date')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Quiz:** {quiz_topic}")
                        st.write(f"**Submitted:** {result.get('submitted_at', 'Unknown')}")
                    
                    with col2:
                        if result.get('status') == 'released':
                            st.write(f"**Score:** {result.get('score_percentage', 0):.1f}%")
                            st.write(f"**Grade:** {result.get('grade', 'F')}")
                        else:
                            st.write("**Status:** Results pending")
                    
                    if result.get('status') == 'released':
                        if result.get('feedback'):
                            st.write(f"**Feedback:** {result.get('feedback')}")
                        
                        # Show detailed results
                        if st.button(f"View Detailed Results", key=f"detail_{result.get('id', '')}"):
                            question_results = result.get('question_results', [])
                            if question_results:
                                st.subheader("Question-by-Question Results")
                                for qr in question_results:
                                    st.write(f"**Q{qr.get('question_number', 0)}:** {'✅' if qr.get('is_correct') else '❌'}")
                                    st.write(f"Your answer: {qr.get('student_answer', 'No answer')}")
                                    st.write(f"Correct answer: {qr.get('correct_answer', 'Unknown')}")
                                    if qr.get('feedback'):
                                        st.write(f"Feedback: {qr.get('feedback')}")
                                    st.write("---")
        else:
            st.info("You haven't taken any quizzes yet.")
    
    def show_profile(self):
        """Display and edit student profile"""
        st.header("👤 My Profile")
        
        user = st.session_state.user
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Profile Information")
            st.write(f"**Name:** {user.get('name', 'Unknown')}")
            st.write(f"**Email:** {user.get('email', 'Unknown')}")
            st.write(f"**Student ID:** {user.get('id', 'Unknown')}")
        
        with col2:
            st.subheader("Statistics")
            student_id = user.get("id", "")
            results = self.firebase_manager.get_student_results(student_id)
            
            st.write(f"**Quizzes Taken:** {len(results)}")
            
            if results:
                avg_score = sum([r.get('score_percentage', 0) for r in results]) / len(results)
                st.write(f"**Average Score:** {avg_score:.1f}%")
                
                best_score = max([r.get('score_percentage', 0) for r in results])
                st.write(f"**Best Score:** {best_score:.1f}%")
            else:
                st.write("**Average Score:** N/A")
                st.write("**Best Score:** N/A")
        
    
    def show_video_assessment(self):
        """Display video assessment interface"""
        st.header("🎬 Video Assessment")
        
        student_id = st.session_state.user.get("id", "")
        student_email = st.session_state.user.get("email", "")
        
        # Check current video status
        video_status = video_submission_manager.get_student_video_status(student_id)
        
        if video_status["submitted"]:
            st.success("✅ Video Assessment Submitted!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Submission Details")
                st.write(f"**Submitted At:** {video_status.get('submitted_at', 'Unknown')}")
                st.write(f"**Status:** {video_status.get('status', 'Unknown')}")
                st.write(f"**Video Link:** {video_status.get('video_link', 'Unknown')}")
            
            with col2:
                st.subheader("📊 Assessment Results")
                if video_status.get("analysis_completed", False):
                    st.write(f"**Score:** {video_status.get('video_score', 0)}%")
                    st.write(f"**Grade:** {video_status.get('video_grade', 'Pending')}")
                    
                    if video_status.get('video_feedback'):
                        st.subheader("💬 Feedback")
                        st.write(video_status.get('video_feedback', ''))
                else:
                    st.info("🔄 Video analysis in progress...")
            
            st.markdown("---")
            st.info("ℹ️ Only one video submission is allowed per student.")
            
        else:
            st.info("📹 Submit your 2-minute video presentation for assessment")
            
            # Video submission form
            with st.form("video_submission"):
                st.subheader("📤 Submit Video Assessment")
                
                st.markdown("""
                **Instructions:**
                1. Record a 2-minute video presentation on your assigned topic
                2. Upload your video to Google Drive
                3. Make sure the video is publicly accessible (Anyone with the link can view)
                4. Copy and paste the Google Drive link below
                """)
                
                video_link = st.text_input(
                    "Google Drive Video Link",
                    placeholder="https://drive.google.com/file/d/your-file-id/view",
                    help="Make sure your video is publicly accessible"
                )
                
                topic = st.selectbox(
                    "Presentation Topic",
                    [
                        "Artificial Intelligence Fundamentals",
                        "Machine Learning Basics", 
                        "Deep Learning and Neural Networks",
                        "Data Science Applications",
                        "Computer Vision",
                        "Natural Language Processing"
                    ]
                )
                
                submit_button = st.form_submit_button("Submit Video Assessment", type="primary")
                
                if submit_button:
                    if video_link:
                        with st.spinner("Submitting your video..."):
                            result = video_submission_manager.submit_video(
                                student_id=student_id,
                                student_email=student_email,
                                video_link=video_link,
                                topic=topic
                            )
                            
                            if result["success"]:
                                st.success(result["message"])
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(result["message"])
                    else:
                        st.error("Please provide a valid Google Drive link")
    
    def show_final_results(self):
        """Display final combined results"""
        st.header("🏆 Final Results")
        
        student_id = st.session_state.user.get("id", "")
        
        # Check for final result
        final_result = self.firebase_manager.get_student_final_result(student_id)
        
        if final_result:
            st.success("🎉 Your Final Results Are Available!")
            
            # Display results in a nice format
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Quiz Score", f"{final_result.get('quiz_score', 0)}%")
            
            with col2:
                st.metric("Video Score", f"{final_result.get('video_score', 0)}%")
            
            with col3:
                st.metric("Total Score", f"{final_result.get('total_score', 0)}%", 
                         delta=f"Grade: {final_result.get('final_grade', 'F')}")
            
            st.markdown("---")
            
            # Selection status
            if final_result.get('selected', False):
                st.success("🏆 **CONGRATULATIONS!** You have been selected for the AISB program!")
                st.balloons()
                
                st.markdown("""
                ### 🎯 What's Next?
                - You will receive detailed instructions via email within 48 hours
                - Keep this result for your records
                - Prepare for the next phase of the program
                
                **Well done on your excellent performance!** 🌟
                """)
            else:
                st.info("📋 Your results have been recorded. Final selection results will be announced soon.")
            
            # Detailed breakdown
            with st.expander("📊 Detailed Score Breakdown"):
                st.subheader("Quiz Performance")
                quiz_results = self.firebase_manager.get_student_results(student_id)
                if quiz_results:
                    latest_quiz = quiz_results[-1]  # Get latest quiz result
                    st.write(f"**Score:** {latest_quiz.get('score_percentage', 0)}%")
                    st.write(f"**Grade:** {latest_quiz.get('grade', 'F')}")
                    if latest_quiz.get('feedback'):
                        st.write(f"**Feedback:** {latest_quiz.get('feedback', '')}")
                
                st.subheader("Video Assessment Performance")
                video_status = video_submission_manager.get_student_video_status(student_id)
                if video_status["submitted"] and video_status.get("analysis_completed", False):
                    st.write(f"**Score:** {video_status.get('video_score', 0)}%")
                    st.write(f"**Grade:** {video_status.get('video_grade', 'Pending')}")
                    if video_status.get('video_feedback'):
                        st.write(f"**Feedback:** {video_status.get('video_feedback', '')}")
                else:
                    st.write("Video assessment not completed or not analyzed yet.")
                
                st.subheader("Combined Calculation")
                st.write("**Formula:** (Quiz Score × 60%) + (Video Score × 40%) = Total Score")
                quiz_weighted = final_result.get('quiz_score', 0) * 0.6
                video_weighted = final_result.get('video_score', 0) * 0.4
                st.write(f"**Calculation:** ({final_result.get('quiz_score', 0)}% × 60%) + ({final_result.get('video_score', 0)}% × 40%) = {final_result.get('total_score', 0)}%")
        
        else:
            st.info("📋 Final results are not yet available.")
            
            # Show current progress
            st.subheader("📊 Your Current Progress")
            
            # Quiz status
            quiz_results = self.firebase_manager.get_student_results(student_id)
            if quiz_results:
                latest_quiz = quiz_results[-1]
                if latest_quiz.get('status') == 'released':
                    st.success(f"✅ Quiz Completed - Score: {latest_quiz.get('score_percentage', 0)}%")
                else:
                    st.warning("⏳ Quiz submitted - Results pending")
            else:
                st.error("❌ Quiz not completed")
            
            # Video status
            video_status = video_submission_manager.get_student_video_status(student_id)
            if video_status["submitted"]:
                if video_status.get("analysis_completed", False):
                    st.success(f"✅ Video Assessment Completed - Score: {video_status.get('video_score', 0)}%")
                else:
                    st.warning("⏳ Video submitted - Analysis in progress")
            else:
                st.error("❌ Video assessment not submitted")
            
            st.markdown("---")
            st.info("Complete both quiz and video assessment to be eligible for final selection.")

def main():
    student_terminal = StudentTerminal()
    student_terminal.run()

if __name__ == "__main__":
    main()
