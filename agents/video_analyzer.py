"""
Video Analysis Agent using CrewAI for Phase 2
"""
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from typing import Dict, List, Any
import json
import re
import requests
from config.settings import OPENAI_API_KEY

class VideoAnalyzerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,  # Lower temperature for consistent analysis
            api_key=OPENAI_API_KEY
        ) if OPENAI_API_KEY else None
        
        self.agent = Agent(
            role="Video Content Analyzer",
            goal="Analyze video content through transcripts and provide comprehensive assessment of student presentations",
            backstory="""You are an expert educational assessor with extensive experience in evaluating 
            student presentations and video content. You analyze speech patterns, content quality, 
            coherence, and technical accuracy to provide fair and detailed assessments.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def validate_google_drive_link(self, video_link: str) -> Dict[str, Any]:
        """Validate Google Drive link format and accessibility"""
        try:
            # Check if it's a Google Drive link
            drive_patterns = [
                r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
                r'https://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/.*?/d/([a-zA-Z0-9_-]+)'
            ]
            
            file_id = None
            for pattern in drive_patterns:
                match = re.search(pattern, video_link)
                if match:
                    file_id = match.group(1)
                    break
            
            if not file_id:
                return {
                    "valid": False,
                    "message": "Invalid Google Drive link format. Please provide a valid Google Drive video link.",
                    "file_id": None
                }
            
            # Create direct access link
            direct_link = f"https://drive.google.com/file/d/{file_id}/view"
            
            # Basic accessibility check (simplified)
            try:
                response = requests.head(direct_link, timeout=10)
                accessible = response.status_code in [200, 302]
            except:
                accessible = True  # Assume accessible if we can't check
            
            return {
                "valid": True,
                "message": "Valid Google Drive link",
                "file_id": file_id,
                "direct_link": direct_link,
                "accessible": accessible
            }
            
        except Exception as e:
            return {
                "valid": False,
                "message": f"Error validating link: {str(e)}",
                "file_id": None
            }
    
    def extract_transcript_from_video(self, video_link: str) -> str:
        """
        Extract transcript from video (mock implementation)
        In production, this would use services like:
        - Google Speech-to-Text API
        - OpenAI Whisper
        - Azure Speech Services
        """
        try:
            # Mock transcript generation for demonstration
            # In real implementation, you would:
            # 1. Download video from Google Drive
            # 2. Extract audio
            # 3. Use speech-to-text service
            
            mock_transcripts = [
                """Hello, my name is John and I'm here to talk about artificial intelligence. 
                AI is a fascinating field that involves creating machines that can think and learn like humans. 
                There are different types of AI including machine learning, deep learning, and neural networks. 
                Machine learning algorithms can analyze data and make predictions. 
                Deep learning uses neural networks with multiple layers to process complex information. 
                AI has many applications in healthcare, finance, transportation, and education. 
                Thank you for listening to my presentation about artificial intelligence.""",
                
                """Good morning, I want to discuss machine learning fundamentals. 
                Machine learning is a subset of artificial intelligence that enables computers to learn from data. 
                There are three main types: supervised learning, unsupervised learning, and reinforcement learning. 
                Supervised learning uses labeled data to train models for prediction tasks. 
                Unsupervised learning finds patterns in data without labels. 
                Reinforcement learning learns through trial and error with rewards and penalties. 
                Popular algorithms include linear regression, decision trees, and support vector machines. 
                Machine learning is transforming industries and creating new opportunities.""",
                
                """Hi everyone, today I'll explain neural networks and deep learning. 
                Neural networks are inspired by how the human brain processes information. 
                They consist of interconnected nodes called neurons that process and transmit data. 
                Deep learning uses neural networks with many hidden layers to learn complex patterns. 
                Convolutional neural networks are great for image recognition tasks. 
                Recurrent neural networks work well with sequential data like text and speech. 
                Training requires large datasets and significant computational power. 
                Deep learning has revolutionized computer vision, natural language processing, and robotics."""
            ]
            
            # Return a random mock transcript
            import random
            transcript = random.choice(mock_transcripts)
            
            return transcript
            
        except Exception as e:
            print(f"❌ Error extracting transcript: {e}")
            return "Error: Could not extract transcript from video"
    
    def analyze_video_content(self, student_id: str, video_link: str, topic: str = "General") -> Dict[str, Any]:
        """
        Analyze video content and provide comprehensive grading
        """
        try:
            # Step 1: Validate the video link
            validation = self.validate_google_drive_link(video_link)
            if not validation["valid"]:
                return {
                    "success": False,
                    "message": validation["message"],
                    "score": 0,
                    "grade": "F"
                }
            
            # Step 2: Extract transcript
            transcript = self.extract_transcript_from_video(video_link)
            
            if "Error:" in transcript:
                return {
                    "success": False,
                    "message": "Could not process video content",
                    "score": 0,
                    "grade": "F"
                }
            
            # Step 3: Analyze content using CrewAI
            analysis_result = self._analyze_transcript(transcript, topic)
            
            return {
                "success": True,
                "message": "Video analysis completed successfully",
                "transcript": transcript,
                "analysis": analysis_result,
                "score": analysis_result.get("score_percentage", 0),
                "grade": analysis_result.get("grade", "F"),
                "feedback": analysis_result.get("overall_feedback", ""),
                "detailed_analysis": analysis_result.get("detailed_analysis", {}),
                "video_link": video_link,
                "file_id": validation.get("file_id", "")
            }
            
        except Exception as e:
            print(f"❌ Error analyzing video: {e}")
            return {
                "success": False,
                "message": f"Analysis error: {str(e)}",
                "score": 0,
                "grade": "F"
            }
    
    def _analyze_transcript(self, transcript: str, topic: str) -> Dict[str, Any]:
        """Analyze transcript using CrewAI agent"""
        
        task = Task(
            description=f"""
            Analyze the following video transcript for a student presentation on "{topic}":
            
            TRANSCRIPT:
            {transcript}
            
            Evaluation Criteria:
            1. Content Quality (30%): Accuracy, depth, and relevance of information
            2. Clarity & Communication (25%): Clear speech, logical flow, easy to understand
            3. Technical Knowledge (20%): Demonstration of understanding of technical concepts
            4. Structure & Organization (15%): Introduction, body, conclusion, logical progression
            5. Engagement & Delivery (10%): Enthusiasm, confidence, audience engagement
            
            Provide detailed analysis and scoring for each criterion.
            
            Format the output as JSON:
            {{
                "content_quality": {{
                    "score": score_out_of_30,
                    "feedback": "detailed feedback on content quality"
                }},
                "clarity_communication": {{
                    "score": score_out_of_25,
                    "feedback": "detailed feedback on clarity and communication"
                }},
                "technical_knowledge": {{
                    "score": score_out_of_20,
                    "feedback": "detailed feedback on technical knowledge"
                }},
                "structure_organization": {{
                    "score": score_out_of_15,
                    "feedback": "detailed feedback on structure and organization"
                }},
                "engagement_delivery": {{
                    "score": score_out_of_10,
                    "feedback": "detailed feedback on engagement and delivery"
                }},
                "total_score": total_score_out_of_100,
                "score_percentage": percentage_score,
                "grade": "letter_grade_A_to_F",
                "strengths": ["list", "of", "strengths"],
                "areas_for_improvement": ["list", "of", "improvement", "areas"],
                "overall_feedback": "comprehensive overall feedback and suggestions"
            }}
            """,
            agent=self.agent,
            expected_output="A detailed JSON analysis of the video transcript with scores and feedback"
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
                analysis_data = self._parse_analysis_result(str(result))
                return analysis_data
            else:
                # Mock analysis for development
                return self._generate_mock_analysis(transcript, topic)
        except Exception as e:
            print(f"❌ Error in CrewAI analysis: {e}")
            return self._generate_mock_analysis(transcript, topic)
    
    def _parse_analysis_result(self, result: str) -> Dict[str, Any]:
        """Parse the CrewAI analysis result"""
        try:
            # Try to extract JSON from the result
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx]
                analysis_data = json.loads(json_str)
                return analysis_data
            else:
                # If JSON parsing fails, create basic analysis
                return self._create_basic_analysis(result)
        except Exception as e:
            print(f"❌ Error parsing analysis result: {e}")
            return self._create_basic_analysis(result)
    
    def _create_basic_analysis(self, result: str) -> Dict[str, Any]:
        """Create basic analysis when AI parsing fails"""
        # Simple scoring based on transcript length and content
        word_count = len(result.split())
        
        # Basic scoring algorithm
        if word_count > 100:
            score = min(85, 60 + (word_count - 100) * 0.2)
        else:
            score = max(40, word_count * 0.6)
        
        grade = self._calculate_letter_grade(score)
        
        return {
            "content_quality": {"score": score * 0.3, "feedback": "Content analysis based on length and structure"},
            "clarity_communication": {"score": score * 0.25, "feedback": "Communication assessment"},
            "technical_knowledge": {"score": score * 0.2, "feedback": "Technical content evaluation"},
            "structure_organization": {"score": score * 0.15, "feedback": "Structure and flow assessment"},
            "engagement_delivery": {"score": score * 0.1, "feedback": "Delivery evaluation"},
            "total_score": score,
            "score_percentage": round(score, 2),
            "grade": grade,
            "strengths": ["Clear presentation", "Good content coverage"],
            "areas_for_improvement": ["More technical depth", "Better structure"],
            "overall_feedback": f"Your presentation scored {score:.1f}%. Focus on improving technical depth and presentation structure."
        }
    
    def _generate_mock_analysis(self, transcript: str, topic: str) -> Dict[str, Any]:
        """Generate mock analysis for development"""
        word_count = len(transcript.split())
        
        # Mock scoring based on transcript quality
        if "artificial intelligence" in transcript.lower() or "machine learning" in transcript.lower():
            base_score = 78
        elif word_count > 80:
            base_score = 72
        else:
            base_score = 65
        
        # Add some randomness
        import random
        score = base_score + random.randint(-5, 10)
        score = max(0, min(100, score))
        
        grade = self._calculate_letter_grade(score)
        
        return {
            "content_quality": {"score": score * 0.3, "feedback": f"Good coverage of {topic} concepts with clear explanations"},
            "clarity_communication": {"score": score * 0.25, "feedback": "Clear and understandable presentation style"},
            "technical_knowledge": {"score": score * 0.2, "feedback": "Demonstrates solid understanding of technical concepts"},
            "structure_organization": {"score": score * 0.15, "feedback": "Well-organized presentation with logical flow"},
            "engagement_delivery": {"score": score * 0.1, "feedback": "Confident delivery with good pacing"},
            "total_score": score,
            "score_percentage": round(score, 2),
            "grade": grade,
            "strengths": ["Clear explanations", "Good technical knowledge", "Well-structured content"],
            "areas_for_improvement": ["More examples", "Deeper technical analysis", "Better conclusion"],
            "overall_feedback": f"Excellent presentation on {topic}! You demonstrated strong understanding of the concepts. To improve further, consider adding more real-world examples and diving deeper into technical details. Your communication skills are strong, and the presentation was well-organized. Keep up the great work!"
        }
    
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
video_analyzer = VideoAnalyzerAgent()
