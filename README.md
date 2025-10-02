# 🎓 AISB Student Management System

A comprehensive AI-powered student assessment platform built with CrewAI, featuring intelligent quiz generation, video assessment analysis, and automated student selection.

## 🌟 Features

### Phase 1: Core Assessment System
- **🤖 AI Quiz Generation**: CrewAI agents create custom quizzes using OpenAI GPT
- **📝 Multiple Question Types**: MCQ, True/False, and Q&A formats
- **🎯 Intelligent Grading**: Automated scoring with detailed feedback
- **👨‍💼 Admin Dashboard**: Quiz creation, result management, and student oversight
- **🎓 Student Portal**: Quiz taking, result viewing, and progress tracking
- **📧 Email Notifications**: Automated confirmations and result releases
- **💾 Robust Data Storage**: Firebase with local JSON fallback

### Phase 2: Advanced Video Assessment
- **🎬 Video Submissions**: Google Drive integration for 2-minute presentations
- **🤖 AI Content Analysis**: Sophisticated video transcript evaluation
- **📊 Multi-Criteria Scoring**: Content quality, communication, technical knowledge assessment
- **🏆 Combined Results**: Weighted scoring (60% Quiz + 40% Video)
- **🎯 Top Student Selection**: Percentage-based automatic selection
- **📧 Multi-Stage Notifications**: Video confirmation and final selection emails

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google account (for Firebase - optional)
- OpenAI API key
- Email account for notifications

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd "CrewAI Agentic Assignment"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   ```bash
   # Copy the example environment file
   cp env_example.txt .env
   
   # Edit .env with your credentials
   notepad .env  # Windows
   nano .env     # macOS/Linux
   ```

5. **Configure Environment Variables**
   
   Edit `.env` file with your credentials:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Firebase Configuration (Optional - will use local storage if not configured)
   FIREBASE_CREDENTIALS_PATH=path_to_your_firebase_credentials.json
   
   # Email Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   
   # Admin Credentials
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your_secure_password
   
   # Application Settings
   APP_NAME=AISB Student Management System
   DEBUG=False
   ```

6. **Launch the Application**
   ```bash
   # Simple launch (recommended)
   streamlit run main_simple.py
   
   # Alternative methods
   python run.py
   python start_app.py
   ```

## 📚 Usage Guide

### For Administrators

1. **Access Admin Panel**
   - Navigate to the admin section
   - Login with admin credentials

2. **Create Quizzes**
   - Select "Create Quiz" 
   - Choose topic, difficulty, and question count
   - AI generates questions automatically
   - Review and publish

3. **Manage Results**
   - View all student submissions
   - Release quiz results to students
   - Monitor video assessments
   - Select top students for final selection

4. **Video Assessment Management**
   - Review submitted videos
   - Trigger AI analysis
   - View combined quiz + video results
   - Release final selections

### For Students

1. **Registration & Login**
   - Register with name, email, and password
   - Login to access student portal

2. **Take Quizzes**
   - Browse available quizzes
   - Complete assessments
   - Receive immediate feedback (after admin release)

3. **Video Assessment**
   - Navigate to "Video Assessment"
   - Upload 2-minute presentation to Google Drive
   - Submit Google Drive link
   - View AI analysis results

4. **Check Results**
   - "My Results": View quiz scores and feedback
   - "Final Results": See combined scores and selection status

## 🏗️ Architecture

### Core Components

```
AISB Student Management System/
├── agents/                     # CrewAI Agents
│   ├── quiz_generator.py      # AI quiz generation
│   ├── quiz_grader.py         # Intelligent grading
│   ├── video_analyzer.py      # Video content analysis
│   └── email_agent.py         # Email notifications
├── database/                   # Data Management
│   ├── firebase_manager.py    # Firebase integration
│   └── local_storage.py       # Local JSON fallback
├── terminals/                  # User Interfaces
│   ├── admin_terminal.py      # Admin dashboard
│   └── student_terminal.py    # Student portal
├── utils/                      # Utilities
│   ├── auth.py               # Authentication
│   └── video_utils.py        # Video processing
├── config/                     # Configuration
│   └── settings.py           # App settings
├── main_simple.py             # Main application
└── requirements.txt           # Dependencies
```

### AI Agents (CrewAI)

1. **Quiz Generator Agent**
   - Role: Educational content creator
   - Capabilities: Generate contextual questions, multiple formats
   - Integration: OpenAI GPT-3.5/4

2. **Quiz Grader Agent**
   - Role: Assessment evaluator
   - Capabilities: Intelligent scoring, detailed feedback
   - Features: Partial credit, explanation generation

3. **Video Analyzer Agent**
   - Role: Content assessment specialist
   - Capabilities: Transcript analysis, multi-criteria evaluation
   - Scoring: Content (30%), Communication (25%), Technical (20%), Structure (15%), Engagement (10%)

4. **Email Agent**
   - Role: Communication manager
   - Capabilities: Multi-stage notifications, template management
   - Triggers: Registration, submission, results, selection

### Data Storage

- **Primary**: Firebase Firestore (cloud-based)
- **Fallback**: Local JSON files (`local_data/`)
- **Files**: `students.json`, `quizzes.json`, `results.json`, `videos.json`, `final_results.json`

## 🔧 Configuration

### Firebase Setup (Optional)

1. Create Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Generate service account key
4. Download JSON credentials
5. Update `FIREBASE_CREDENTIALS_PATH` in `.env`

### Email Configuration

#### Gmail Setup
1. Enable 2-Factor Authentication
2. Generate App Password: Google Account → Security → App passwords
3. Use app password in `EMAIL_PASSWORD`

#### Other Providers
- Update `SMTP_SERVER` and `SMTP_PORT` accordingly
- Ensure authentication method compatibility

### OpenAI API

1. Create account at [OpenAI](https://platform.openai.com/)
2. Generate API key
3. Add to `OPENAI_API_KEY` in `.env`
4. Ensure sufficient credits for usage

## 📊 Assessment Workflow

### Phase 1: Quiz Assessment
```
Admin Creates Quiz → Student Takes Quiz → AI Grades → Admin Releases Results
```

### Phase 2: Video Assessment
```
Student Submits Video → AI Analyzes Content → Combined Scoring → Top Student Selection
```

### Scoring Formula
```
Final Score = (Quiz Score × 60%) + (Video Score × 40%)
```

## 🛠️ Troubleshooting

### Common Issues

1. **Firebase Connection Failed**
   - Solution: System automatically falls back to local storage
   - Check: Firebase credentials and API enablement

2. **OpenAI API Errors**
   - Check: API key validity and credit balance
   - Fallback: Mock responses for development

3. **Email Sending Failed**
   - Verify: SMTP settings and app passwords
   - Check: Firewall and antivirus settings

4. **Streamlit Import Errors**
   - Solution: Use `main_simple.py` instead of `main.py`
   - Install: Missing dependencies from `requirements.txt`

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=True
```

This provides:
- Detailed error messages
- Mock data for testing
- Enhanced logging

## 📁 File Structure

### Important Files

- **`main_simple.py`**: Primary application entry point
- **`requirements.txt`**: Python dependencies
- **`.env`**: Environment configuration (create from `env_example.txt`)
- **`local_data/`**: Local database storage (auto-created)

### Generated Data

The system creates these data files automatically:
- `local_data/students.json`: Student registrations
- `local_data/quizzes.json`: Generated quizzes
- `local_data/results.json`: Quiz results
- `local_data/videos.json`: Video submissions and analysis
- `local_data/final_results.json`: Combined final results

## 🔒 Security & Privacy

### Data Protection
- Personal data stored locally by default
- Firebase integration optional
- Comprehensive `.gitignore` prevents credential exposure

### Authentication
- Bcrypt password hashing
- Session management
- Admin/student role separation

### Best Practices
- Never commit `.env` files
- Use app passwords for email
- Regular credential rotation
- Monitor API usage

## 🚀 Deployment

### Local Development
```bash
streamlit run main_simple.py
```

### Production Deployment

#### Heroku
1. Create `Procfile`:
   ```
   web: streamlit run main_simple.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Deploy with environment variables

#### Docker
1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "main_simple.py"]
   ```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Follow existing code structure
4. Test thoroughly
5. Submit pull request

### Code Standards
- Follow PEP 8 for Python
- Document functions and classes
- Use type hints where applicable
- Maintain error handling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help
1. Check troubleshooting section
2. Review configuration settings
3. Verify environment setup
4. Check system logs

### Contact
- Create GitHub issues for bugs
- Feature requests welcome
- Documentation improvements appreciated

## 🎯 Roadmap

### Planned Features
- [ ] Real-time video processing
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Batch student import
- [ ] Custom grading rubrics

### Version History
- **v2.0**: Phase 2 - Video Assessment System
- **v1.0**: Phase 1 - Core Quiz Management

---

**Built with ❤️ using CrewAI, Streamlit, and OpenAI**

*For technical support or feature requests, please create an issue in the repository.*