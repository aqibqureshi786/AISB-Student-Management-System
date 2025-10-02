"""
Email Notification Agent using CrewAI
"""
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any
from config.settings import OPENAI_API_KEY, SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

class EmailAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=OPENAI_API_KEY
        ) if OPENAI_API_KEY else None
        
        self.agent = Agent(
            role="Email Communication Specialist",
            goal="Create professional and engaging email content for student notifications",
            backstory="""You are a professional communication specialist with expertise in 
            educational correspondence. You create clear, encouraging, and informative emails 
            that maintain a positive tone while delivering important information to students.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def send_registration_confirmation(self, student_email: str, student_name: str) -> bool:
        """Send registration confirmation email"""
        subject = "Welcome to AISB - Registration Confirmed!"
        
        content = self._generate_email_content(
            email_type="registration_confirmation",
            student_name=student_name,
            additional_info={}
        )
        
        return self._send_email(student_email, subject, content)
    
    def send_quiz_submission_confirmation(self, student_email: str, student_name: str, 
                                        quiz_topic: str, submission_time: str) -> bool:
        """Send quiz submission confirmation email"""
        subject = f"Quiz Submission Confirmed - {quiz_topic}"
        
        content = self._generate_email_content(
            email_type="quiz_submission",
            student_name=student_name,
            additional_info={
                "quiz_topic": quiz_topic,
                "submission_time": submission_time
            }
        )
        
        return self._send_email(student_email, subject, content)
    
    def send_result_notification(self, student_email: str, student_name: str, 
                               quiz_topic: str, score: float, grade: str, feedback: str) -> bool:
        """Send quiz result notification email"""
        subject = f"Quiz Results Available - {quiz_topic}"
        
        content = self._generate_email_content(
            email_type="result_notification",
            student_name=student_name,
            additional_info={
                "quiz_topic": quiz_topic,
                "score": score,
                "grade": grade,
                "feedback": feedback
            }
        )
        
        return self._send_email(student_email, subject, content)
    
    def send_bulk_results(self, student_results: List[Dict[str, Any]], quiz_topic: str) -> Dict[str, bool]:
        """Send results to multiple students"""
        results = {}
        
        for result in student_results:
            success = self.send_result_notification(
                student_email=result.get("email", ""),
                student_name=result.get("name", ""),
                quiz_topic=quiz_topic,
                score=result.get("score", 0),
                grade=result.get("grade", "F"),
                feedback=result.get("feedback", "")
            )
            results[result.get("email", "")] = success
        
        return results
    
    def _generate_email_content(self, email_type: str, student_name: str, 
                              additional_info: Dict[str, Any]) -> str:
        """Generate email content using AI agent"""
        
        if email_type == "registration_confirmation":
            prompt = f"""
            Create a welcoming registration confirmation email for a student named {student_name} 
            who has just registered for the AISB (Artificial Intelligence Student Body) Student Management System.
            
            Include:
            - Welcome message
            - Brief overview of what they can expect
            - Instructions for logging in
            - Contact information for support
            
            Keep the tone professional but friendly and encouraging.
            """
        
        elif email_type == "quiz_submission":
            prompt = f"""
            Create a quiz submission confirmation email for {student_name} who just submitted 
            a quiz on "{additional_info.get('quiz_topic', 'Unknown Topic')}" at 
            {additional_info.get('submission_time', 'Unknown Time')}.
            
            Include:
            - Confirmation of successful submission
            - Quiz topic and submission time
            - Information about when results will be available
            - Encouragement and next steps
            
            Keep the tone supportive and informative.
            """
        
        elif email_type == "result_notification":
            prompt = f"""
            Create a quiz result notification email for {student_name} with the following details:
            - Quiz Topic: {additional_info.get('quiz_topic', 'Unknown')}
            - Score: {additional_info.get('score', 0)}%
            - Grade: {additional_info.get('grade', 'F')}
            - Feedback: {additional_info.get('feedback', 'No feedback available')}
            
            Include:
            - Congratulations or encouragement based on performance
            - Detailed results
            - Constructive feedback
            - Motivation for continued learning
            
            Keep the tone positive and constructive, regardless of the score.
            """
        
        else:
            return f"Hello {student_name},\n\nThank you for using the AISB Student Management System.\n\nBest regards,\nAISB Team"
        
        # Create task for email content generation
        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="A well-formatted, professional email content"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        try:
            if self.llm:
                result = crew.kickoff()
                return str(result)
            else:
                # Mock email content for development
                return self._generate_mock_email_content(email_type, student_name, additional_info)
        except Exception as e:
            print(f"Error generating email content: {e}")
            return self._generate_mock_email_content(email_type, student_name, additional_info)
    
    def _generate_mock_email_content(self, email_type: str, student_name: str, 
                                   additional_info: Dict[str, Any]) -> str:
        """Generate mock email content for development"""
        
        if email_type == "registration_confirmation":
            return f"""
Dear {student_name},

Welcome to the AISB (Artificial Intelligence Student Body) Student Management System!

Your registration has been successfully completed. You can now log in to access quizzes, view your results, and track your progress.

To get started:
1. Log in using your registered email and password
2. Browse available quizzes
3. Take quizzes at your own pace
4. View your results once they are released

If you have any questions or need assistance, please don't hesitate to contact our support team.

Best regards,
AISB Team
            """
        
        elif email_type == "quiz_submission":
            return f"""
Dear {student_name},

This email confirms that you have successfully submitted your quiz on "{additional_info.get('quiz_topic', 'Unknown Topic')}" 
at {additional_info.get('submission_time', 'Unknown Time')}.

Your submission has been recorded and will be graded shortly. Results will be made available once the admin releases them.

Thank you for your participation!

Best regards,
AISB Team
            """
        
        elif email_type == "result_notification":
            return f"""
Dear {student_name},

Your quiz results for "{additional_info.get('quiz_topic', 'Unknown')}" are now available!

Results:
- Score: {additional_info.get('score', 0)}%
- Grade: {additional_info.get('grade', 'F')}

Feedback: {additional_info.get('feedback', 'No feedback available')}

Keep up the great work and continue learning!

Best regards,
AISB Team
            """
        
        return f"Hello {student_name},\n\nThank you for using the AISB Student Management System.\n\nBest regards,\nAISB Team"
    
    def _send_email(self, recipient_email: str, subject: str, content: str) -> bool:
        """Send email using SMTP"""
        try:
            if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
                print(f"Mock: Sending email to {recipient_email}")
                print(f"Subject: {subject}")
                print(f"Content: {content[:100]}...")
                return True
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(content, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Enable security
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            
            # Send email
            text = msg.as_string()
            server.sendmail(EMAIL_ADDRESS, recipient_email, text)
            server.quit()
            
            print(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")
            return False

# Global instance
email_agent = EmailAgent()
