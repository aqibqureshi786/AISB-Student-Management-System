"""
Admin Terminal for AISB Student Management System
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go

from utils.auth import auth_manager
from database.firebase_manager import firebase_manager
from agents.quiz_generator import quiz_generator
from agents.quiz_grader import quiz_grader
from agents.email_agent import email_agent

class AdminTerminal:
    def __init__(self):
        self.auth_manager = auth_manager
        self.firebase_manager = firebase_manager
        self.quiz_generator = quiz_generator
        self.quiz_grader = quiz_grader
        self.email_agent = email_agent
    
    def run(self):
        """Main admin terminal interface"""
        st.set_page_config(
            page_title="AISB Admin Terminal",
            page_icon="👨‍💼",
            layout="wide"
        )
        
        st.title("🎓 AISB Admin Terminal")
        st.markdown("---")
        
        # Check if admin is logged in
        if "admin" not in st.session_state:
            self.show_login()
        else:
            self.show_admin_dashboard()
    
    def show_login(self):
        """Display admin login form"""
        st.subheader("🔐 Admin Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("admin_login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Login")
                
                if submit_button:
                    if username and password:
                        result = self.auth_manager.login_admin(username, password)
                        
                        if result["success"]:
                            st.session_state.admin = result["admin"]
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(result["message"])
                    else:
                        st.error("Please enter both username and password")
    
    def show_admin_dashboard(self):
        """Display main admin dashboard"""
        # Sidebar navigation
        st.sidebar.title("Navigation")
        admin_name = st.session_state.admin.get("username", "Admin")
        st.sidebar.write(f"Welcome, {admin_name}!")
        
        menu_options = [
            "Dashboard",
            "Create Quiz",
            "View Quizzes", 
            "Student Results",
            "Release Results",
            "Analytics"
        ]
        
        selected_option = st.sidebar.selectbox("Select Option", menu_options)
        
        if st.sidebar.button("Logout"):
            self.auth_manager.logout()
        
        # Main content based on selection
        if selected_option == "Dashboard":
            self.show_dashboard_overview()
        elif selected_option == "Create Quiz":
            self.show_create_quiz()
        elif selected_option == "View Quizzes":
            self.show_view_quizzes()
        elif selected_option == "Student Results":
            self.show_student_results()
        elif selected_option == "Release Results":
            self.show_release_results()
        elif selected_option == "Analytics":
            self.show_analytics()
    
    def show_dashboard_overview(self):
        """Display dashboard overview"""
        st.header("📊 Dashboard Overview")
        
        # Get statistics
        quizzes = self.firebase_manager.get_all_quizzes()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Quizzes", len(quizzes))
        
        with col2:
            # Count total results across all quizzes
            total_submissions = 0
            for quiz in quizzes:
                results = self.firebase_manager.get_results_by_quiz(quiz.get("id", ""))
                total_submissions += len(results)
            st.metric("Total Submissions", total_submissions)
        
        with col3:
            # Count active students (mock for now)
            st.metric("Active Students", "25")
        
        with col4:
            # Average score (mock for now)
            st.metric("Average Score", "78%")
        
        st.markdown("---")
        
        # Recent activity
        st.subheader("📋 Recent Quizzes")
        if quizzes:
            quiz_df = pd.DataFrame([
                {
                    "Topic": quiz.get("topic", "Unknown"),
                    "Questions": quiz.get("total_questions", 0),
                    "Difficulty": quiz.get("difficulty", "Unknown"),
                    "Type": quiz.get("question_type", "Unknown"),
                    "Created": "Recently"  # You can add timestamp to quiz data
                }
                for quiz in quizzes[-5:]  # Show last 5 quizzes
            ])
            st.dataframe(quiz_df, use_container_width=True)
        else:
            st.info("No quizzes created yet. Create your first quiz!")
    
    def show_create_quiz(self):
        """Display quiz creation interface"""
        st.header("📝 Create New Quiz")
        
        with st.form("create_quiz"):
            col1, col2 = st.columns(2)
            
            with col1:
                topic = st.text_input("Quiz Topic", placeholder="e.g., Artificial Intelligence")
                num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
            
            with col2:
                difficulty = st.selectbox("Difficulty Level", ["easy", "medium", "hard"])
                question_type = st.selectbox("Question Type", ["MCQ", "True/False", "Q/A"])
            
            description = st.text_area("Quiz Description (Optional)", 
                                     placeholder="Brief description of the quiz content...")
            
            submit_button = st.form_submit_button("Generate Quiz", type="primary")
            
            if submit_button:
                if topic and num_questions:
                    with st.spinner("Generating quiz... This may take a moment."):
                        # Generate quiz using AI agent
                        quiz_data = self.quiz_generator.generate_quiz(
                            topic=topic,
                            num_questions=num_questions,
                            difficulty=difficulty,
                            question_type=question_type
                        )
                        
                        # Add metadata
                        quiz_data.update({
                            "description": description,
                            "created_at": datetime.now().isoformat(),
                            "created_by": st.session_state.admin.get("username", "admin"),
                            "status": "active"
                        })
                        
                        # Save to database
                        quiz_id = self.firebase_manager.add_quiz(quiz_data)
                        
                        if quiz_id:
                            st.success(f"Quiz created successfully! Quiz ID: {quiz_id}")
                            
                            # Display generated quiz
                            st.subheader("Generated Quiz Preview")
                            self.display_quiz_preview(quiz_data)
                        else:
                            st.error("Failed to save quiz to database")
                else:
                    st.error("Please fill in all required fields")
    
    def display_quiz_preview(self, quiz_data: Dict[str, Any]):
        """Display a preview of the generated quiz"""
        st.write(f"**Topic:** {quiz_data.get('topic', 'Unknown')}")
        st.write(f"**Difficulty:** {quiz_data.get('difficulty', 'Unknown')}")
        st.write(f"**Type:** {quiz_data.get('question_type', 'Unknown')}")
        st.write(f"**Total Questions:** {quiz_data.get('total_questions', 0)}")
        
        questions = quiz_data.get('questions', [])
        
        for i, question in enumerate(questions[:3]):  # Show first 3 questions
            st.write(f"**Question {i + 1}:** {question.get('question', 'No question')}")
            
            if question.get('options'):
                for option in question['options']:
                    st.write(f"  {option}")
            
            st.write(f"**Correct Answer:** {question.get('correct_answer', 'No answer')}")
            st.write("---")
        
        if len(questions) > 3:
            st.write(f"... and {len(questions) - 3} more questions")
    
    def show_view_quizzes(self):
        """Display all created quizzes"""
        st.header("📚 All Quizzes")
        
        quizzes = self.firebase_manager.get_all_quizzes()
        
        if quizzes:
            for quiz in quizzes:
                with st.expander(f"📝 {quiz.get('topic', 'Unknown Topic')} - {quiz.get('difficulty', 'Unknown')} Level"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Questions:** {quiz.get('total_questions', 0)}")
                        st.write(f"**Type:** {quiz.get('question_type', 'Unknown')}")
                        st.write(f"**Created:** {quiz.get('created_at', 'Unknown')}")
                    
                    with col2:
                        st.write(f"**Created by:** {quiz.get('created_by', 'Unknown')}")
                        st.write(f"**Status:** {quiz.get('status', 'Unknown')}")
                        
                        # Get submission count
                        results = self.firebase_manager.get_results_by_quiz(quiz.get('id', ''))
                        st.write(f"**Submissions:** {len(results)}")
                    
                    if quiz.get('description'):
                        st.write(f"**Description:** {quiz.get('description')}")
                    
                    # Show questions
                    if st.button(f"View Questions", key=f"view_{quiz.get('id', '')}"):
                        questions = quiz.get('questions', [])
                        for i, question in enumerate(questions):
                            st.write(f"**Q{i + 1}:** {question.get('question', 'No question')}")
                            if question.get('options'):
                                for option in question['options']:
                                    st.write(f"  {option}")
                            st.write(f"**Answer:** {question.get('correct_answer', 'No answer')}")
                            st.write("---")
        else:
            st.info("No quizzes found. Create your first quiz!")
    
    def show_student_results(self):
        """Display student results for all quizzes"""
        st.header("📊 Student Results")
        
        quizzes = self.firebase_manager.get_all_quizzes()
        
        if not quizzes:
            st.info("No quizzes found.")
            return
        
        # Quiz selection
        quiz_options = {f"{quiz.get('topic', 'Unknown')} ({quiz.get('id', '')})": quiz.get('id', '') 
                       for quiz in quizzes}
        
        selected_quiz_display = st.selectbox("Select Quiz", list(quiz_options.keys()))
        selected_quiz_id = quiz_options[selected_quiz_display]
        
        # Get results for selected quiz
        results = self.firebase_manager.get_results_by_quiz(selected_quiz_id)
        
        if results:
            # Display results table
            results_data = []
            for result in results:
                results_data.append({
                    "Student ID": result.get("student_id", "Unknown"),
                    "Score": f"{result.get('score_percentage', 0):.1f}%",
                    "Grade": result.get("grade", "F"),
                    "Submitted": result.get("submitted_at", "Unknown"),
                    "Status": result.get("status", "pending")
                })
            
            results_df = pd.DataFrame(results_data)
            st.dataframe(results_df, use_container_width=True)
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_score = sum([r.get('score_percentage', 0) for r in results]) / len(results)
                st.metric("Average Score", f"{avg_score:.1f}%")
            
            with col2:
                passed = len([r for r in results if r.get('score_percentage', 0) >= 60])
                st.metric("Students Passed", f"{passed}/{len(results)}")
            
            with col3:
                released = len([r for r in results if r.get('status') == 'released'])
                st.metric("Results Released", f"{released}/{len(results)}")
        else:
            st.info("No submissions found for this quiz.")
    
    def show_release_results(self):
        """Interface for releasing results to students"""
        st.header("📤 Release Results")
        
        quizzes = self.firebase_manager.get_all_quizzes()
        
        if not quizzes:
            st.info("No quizzes found.")
            return
        
        # Quiz selection
        quiz_options = {f"{quiz.get('topic', 'Unknown')} ({quiz.get('id', '')})": quiz.get('id', '') 
                       for quiz in quizzes}
        
        selected_quiz_display = st.selectbox("Select Quiz", list(quiz_options.keys()))
        selected_quiz_id = quiz_options[selected_quiz_display]
        
        # Get results
        results = self.firebase_manager.get_results_by_quiz(selected_quiz_id)
        
        if results:
            st.subheader("Filter Students for Result Release")
            
            col1, col2 = st.columns(2)
            
            with col1:
                min_score = st.number_input("Minimum Score (%)", min_value=0, max_value=100, value=80)
            
            with col2:
                release_all = st.checkbox("Release to All Students")
            
            # Filter results
            if release_all:
                filtered_results = results
            else:
                filtered_results = [r for r in results if r.get('score_percentage', 0) >= min_score]
            
            st.write(f"**Students to receive results:** {len(filtered_results)}")
            
            if filtered_results:
                # Display filtered students
                for result in filtered_results:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"Student ID: {result.get('student_id', 'Unknown')}")
                    
                    with col2:
                        st.write(f"Score: {result.get('score_percentage', 0):.1f}%")
                    
                    with col3:
                        st.write(f"Grade: {result.get('grade', 'F')}")
                
                if st.button("Release Results & Send Emails", type="primary"):
                    with st.spinner("Releasing results and sending emails..."):
                        success_count = 0
                        
                        for result in filtered_results:
                            # Update result status
                            if self.firebase_manager.update_result_status(result.get('id', ''), 'released'):
                                success_count += 1
                                
                                # Send email (mock for now)
                                # In real implementation, you'd get student email from database
                                # email_sent = self.email_agent.send_result_notification(...)
                        
                        st.success(f"Results released to {success_count} students!")
            else:
                st.info("No students match the selected criteria.")
        else:
            st.info("No submissions found for this quiz.")
    
    def show_analytics(self):
        """Display analytics and charts"""
        st.header("📈 Analytics")
        
        quizzes = self.firebase_manager.get_all_quizzes()
        
        if not quizzes:
            st.info("No data available for analytics.")
            return
        
        # Quiz performance chart
        quiz_performance = []
        for quiz in quizzes:
            results = self.firebase_manager.get_results_by_quiz(quiz.get('id', ''))
            if results:
                avg_score = sum([r.get('score_percentage', 0) for r in results]) / len(results)
                quiz_performance.append({
                    'Quiz': quiz.get('topic', 'Unknown'),
                    'Average Score': avg_score,
                    'Submissions': len(results)
                })
        
        if quiz_performance:
            df = pd.DataFrame(quiz_performance)
            
            # Bar chart for average scores
            fig = px.bar(df, x='Quiz', y='Average Score', 
                        title='Average Scores by Quiz',
                        color='Average Score',
                        color_continuous_scale='viridis')
            st.plotly_chart(fig, use_container_width=True)
            
            # Submissions chart
            fig2 = px.bar(df, x='Quiz', y='Submissions',
                         title='Number of Submissions by Quiz',
                         color='Submissions',
                         color_continuous_scale='blues')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No quiz results available for analytics.")

def main():
    admin_terminal = AdminTerminal()
    admin_terminal.run()

if __name__ == "__main__":
    main()
