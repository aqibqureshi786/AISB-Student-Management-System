"""
Quiz Generation Agent using CrewAI
"""
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from typing import Dict, List, Any
import json
from config.settings import OPENAI_API_KEY

class QuizGeneratorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=OPENAI_API_KEY
        ) if OPENAI_API_KEY else None
        
        self.agent = Agent(
            role="Quiz Generator",
            goal="Generate educational quizzes based on specified topics, difficulty levels, and question types",
            backstory="""You are an expert educational content creator with years of experience in 
            developing engaging and challenging quiz questions. You understand different learning levels 
            and can create questions that test both knowledge and understanding.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def generate_quiz(self, topic: str, num_questions: int, difficulty: str, question_type: str) -> Dict[str, Any]:
        """
        Generate a quiz based on the given parameters
        
        Args:
            topic: The subject topic for the quiz
            num_questions: Number of questions to generate
            difficulty: easy, medium, or hard
            question_type: MCQ, True/False, or Q/A
        
        Returns:
            Dictionary containing the generated quiz
        """
        
        # Create the task for quiz generation
        task = Task(
            description=f"""
            Generate a {difficulty} level quiz on the topic '{topic}' with {num_questions} questions.
            Question type: {question_type}
            
            Requirements:
            1. Each question should be clear and unambiguous
            2. For MCQ: Provide 4 options (A, B, C, D) with one correct answer
            3. For True/False: Provide a statement that can be clearly true or false
            4. For Q/A: Provide open-ended questions with sample answers
            5. Include the correct answer for each question
            6. Ensure questions are appropriate for the {difficulty} difficulty level
            
            Format the output as a JSON structure with:
            {{
                "topic": "{topic}",
                "difficulty": "{difficulty}",
                "question_type": "{question_type}",
                "total_questions": {num_questions},
                "questions": [
                    {{
                        "question_number": 1,
                        "question": "Question text here",
                        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                        "correct_answer": "A",
                        "explanation": "Brief explanation of the correct answer"
                    }}
                ]
            }}
            """,
            agent=self.agent,
            expected_output="A well-formatted JSON quiz with the specified number of questions"
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
                # Parse the result and return as dictionary
                quiz_data = self._parse_quiz_result(str(result), topic, difficulty, question_type, num_questions)
                return quiz_data
            else:
                # Mock quiz for development without API key
                return self._generate_mock_quiz(topic, num_questions, difficulty, question_type)
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return self._generate_mock_quiz(topic, num_questions, difficulty, question_type)
    
    def _parse_quiz_result(self, result: str, topic: str, difficulty: str, question_type: str, num_questions: int) -> Dict[str, Any]:
        """Parse the LLM result and extract quiz data"""
        try:
            # Try to extract JSON from the result
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx]
                quiz_data = json.loads(json_str)
                return quiz_data
            else:
                # If JSON parsing fails, create structured data from text
                return self._create_quiz_from_text(result, topic, difficulty, question_type, num_questions)
        except Exception as e:
            print(f"Error parsing quiz result: {e}")
            return self._generate_mock_quiz(topic, num_questions, difficulty, question_type)
    
    def _create_quiz_from_text(self, text: str, topic: str, difficulty: str, question_type: str, num_questions: int) -> Dict[str, Any]:
        """Create quiz structure from plain text result"""
        lines = text.split('\n')
        questions = []
        
        current_question = {}
        question_count = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                if current_question and question_count < num_questions:
                    questions.append(current_question)
                    question_count += 1
                
                current_question = {
                    "question_number": question_count + 1,
                    "question": line[2:].strip(),
                    "options": [],
                    "correct_answer": "A",
                    "explanation": "Generated explanation"
                }
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                if current_question:
                    current_question["options"].append(line)
        
        if current_question and question_count < num_questions:
            questions.append(current_question)
        
        return {
            "topic": topic,
            "difficulty": difficulty,
            "question_type": question_type,
            "total_questions": len(questions),
            "questions": questions
        }
    
    def _generate_mock_quiz(self, topic: str, num_questions: int, difficulty: str, question_type: str) -> Dict[str, Any]:
        """Generate a mock quiz for development/testing"""
        questions = []
        
        for i in range(num_questions):
            if question_type == "MCQ":
                question = {
                    "question_number": i + 1,
                    "question": f"Sample {difficulty} MCQ question {i + 1} about {topic}?",
                    "options": [
                        "A) Option 1",
                        "B) Option 2", 
                        "C) Option 3",
                        "D) Option 4"
                    ],
                    "correct_answer": "A",
                    "explanation": f"This is the explanation for question {i + 1}"
                }
            elif question_type == "True/False":
                question = {
                    "question_number": i + 1,
                    "question": f"Sample {difficulty} True/False statement {i + 1} about {topic}.",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": f"This is the explanation for question {i + 1}"
                }
            else:  # Q/A
                question = {
                    "question_number": i + 1,
                    "question": f"Sample {difficulty} Q/A question {i + 1} about {topic}?",
                    "options": [],
                    "correct_answer": f"Sample answer for question {i + 1}",
                    "explanation": f"This is the explanation for question {i + 1}"
                }
            
            questions.append(question)
        
        return {
            "topic": topic,
            "difficulty": difficulty,
            "question_type": question_type,
            "total_questions": num_questions,
            "questions": questions
        }

# Global instance
quiz_generator = QuizGeneratorAgent()
