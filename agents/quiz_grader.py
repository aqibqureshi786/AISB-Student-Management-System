"""
Quiz Grading Agent using CrewAI
"""
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from typing import Dict, List, Any
import json
from config.settings import OPENAI_API_KEY

class QuizGraderAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,  # Lower temperature for consistent grading
            api_key=OPENAI_API_KEY
        ) if OPENAI_API_KEY else None
        
        self.agent = Agent(
            role="Quiz Grader",
            goal="Grade student quiz submissions accurately and provide detailed feedback",
            backstory="""You are an experienced educator and assessment specialist with expertise in 
            evaluating student responses. You provide fair, consistent, and detailed feedback on quiz 
            submissions, helping students understand their mistakes and learn from them.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def grade_quiz(self, student_answers: List[str], correct_answers: List[str], 
                   questions: List[Dict[str, Any]], question_type: str) -> Dict[str, Any]:
        """
        Grade a student's quiz submission
        
        Args:
            student_answers: List of student's answers
            correct_answers: List of correct answers
            questions: List of question data
            question_type: Type of questions (MCQ, True/False, Q/A)
        
        Returns:
            Dictionary containing grading results
        """
        
        # Create the task for quiz grading
        task = Task(
            description=f"""
            Grade the following quiz submission for {question_type} questions:
            
            Questions and Answers:
            {self._format_questions_for_grading(questions, student_answers, correct_answers)}
            
            Requirements:
            1. Compare each student answer with the correct answer
            2. For MCQ and True/False: Award full points for exact matches, zero for incorrect
            3. For Q/A: Evaluate based on content accuracy and completeness (partial credit allowed)
            4. Calculate total score as percentage
            5. Provide feedback for each question
            6. Identify areas for improvement
            
            Format the output as JSON:
            {{
                "total_questions": {len(questions)},
                "correct_answers": number_of_correct_answers,
                "score_percentage": calculated_percentage,
                "question_results": [
                    {{
                        "question_number": 1,
                        "student_answer": "student's answer",
                        "correct_answer": "correct answer",
                        "is_correct": true/false,
                        "points_earned": points_out_of_total,
                        "feedback": "specific feedback for this question"
                    }}
                ],
                "overall_feedback": "general feedback and suggestions for improvement",
                "grade": "letter grade (A, B, C, D, F)"
            }}
            """,
            agent=self.agent,
            expected_output="A detailed grading report in JSON format"
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
                grading_result = self._parse_grading_result(str(result), student_answers, correct_answers, questions)
                return grading_result
            else:
                # Mock grading for development
                return self._generate_mock_grading(student_answers, correct_answers, questions, question_type)
        except Exception as e:
            print(f"Error grading quiz: {e}")
            return self._generate_mock_grading(student_answers, correct_answers, questions, question_type)
    
    def _format_questions_for_grading(self, questions: List[Dict[str, Any]], 
                                    student_answers: List[str], correct_answers: List[str]) -> str:
        """Format questions and answers for the grading prompt"""
        formatted = ""
        for i, question in enumerate(questions):
            formatted += f"\nQuestion {i + 1}: {question.get('question', '')}\n"
            formatted += f"Student Answer: {student_answers[i] if i < len(student_answers) else 'No answer'}\n"
            formatted += f"Correct Answer: {correct_answers[i] if i < len(correct_answers) else 'N/A'}\n"
            formatted += "---\n"
        return formatted
    
    def _parse_grading_result(self, result: str, student_answers: List[str], 
                            correct_answers: List[str], questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse the LLM grading result"""
        try:
            # Try to extract JSON from the result
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx]
                grading_data = json.loads(json_str)
                return grading_data
            else:
                # If JSON parsing fails, create basic grading
                return self._create_basic_grading(student_answers, correct_answers, questions)
        except Exception as e:
            print(f"Error parsing grading result: {e}")
            return self._create_basic_grading(student_answers, correct_answers, questions)
    
    def _create_basic_grading(self, student_answers: List[str], correct_answers: List[str], 
                            questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create basic grading when AI parsing fails"""
        correct_count = 0
        question_results = []
        
        for i, question in enumerate(questions):
            student_answer = student_answers[i] if i < len(student_answers) else ""
            correct_answer = correct_answers[i] if i < len(correct_answers) else ""
            
            is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
            if is_correct:
                correct_count += 1
            
            question_results.append({
                "question_number": i + 1,
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "points_earned": 1 if is_correct else 0,
                "feedback": "Correct!" if is_correct else f"Incorrect. The correct answer is: {correct_answer}"
            })
        
        score_percentage = (correct_count / len(questions)) * 100 if questions else 0
        grade = self._calculate_letter_grade(score_percentage)
        
        return {
            "total_questions": len(questions),
            "correct_answers": correct_count,
            "score_percentage": round(score_percentage, 2),
            "question_results": question_results,
            "overall_feedback": f"You scored {correct_count}/{len(questions)} ({score_percentage:.1f}%)",
            "grade": grade
        }
    
    def _generate_mock_grading(self, student_answers: List[str], correct_answers: List[str], 
                             questions: List[Dict[str, Any]], question_type: str) -> Dict[str, Any]:
        """Generate mock grading for development"""
        return self._create_basic_grading(student_answers, correct_answers, questions)
    
    def _calculate_letter_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"

# Global instance
quiz_grader = QuizGraderAgent()
