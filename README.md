# SDGP Project Scraper & AI Chatbot

A comprehensive Python tool to scrape all projects from the Software Development Group Project (SDGP) website and provide an intelligent AI-powered chatbot for project analysis and insights.

## 🚀 Features

- 🔍 **Complete Project Scraping**: Fetches all projects from the SDGP website (200+ projects)
- 📊 **Detailed Information**: Retrieves comprehensive project details including team info, tech stack, and more
- 🤖 **AI-Powered Analysis**: Intelligent chatbot with Google Vertex AI for project insights
- 💾 **Smart Caching**: Efficient caching system for AI responses to reduce API calls
- 🔗 **Direct Project Links**: Direct links to official SDGP project pages
- 📈 **Advanced Analytics**: Detailed project analysis with trends and insights
- 🎯 **Conversation Memory**: Context-aware responses with conversation history
- ⚙️ **Easy Setup**: Simple setup process with environment configuration

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Vertex AI API enabled
- Google Cloud Service Account with appropriate permissions

## 🛠️ Quick Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd FYP_Data_Trace
```

### 2. Run the Setup Script
```bash
python setup.py
```

The setup script will:
- ✅ Check Python version compatibility
- 📦 Install required dependencies
- 📁 Create necessary directories
- 🔐 Guide you through Google Cloud credentials setup
- ⚙️ Create environment configuration file

### 3. Configure Google Cloud

1. **Create a Google Cloud Project** (or use existing)
2. **Enable Vertex AI API**
3. **Create a Service Account** with `Vertex AI User` role
4. **Download the JSON key file**
5. **Place it in the `credentials/` folder** as `service-account-key.json`

📖 **Detailed Setup Guide**: See [AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md) for step-by-step instructions.

### 4. Configure Environment Variables

Edit the `.env` file created by the setup script:

```env
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account-key.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional: Customize behavior
SCRAPER_DELAY=1.0
AI_MODEL_NAME=gemini-2.0-flash-exp
AI_CACHE_ENABLED=true
```

## 🎯 Usage

### 1. Scrape Project Data
```bash
python run_scraper.py
```

This will:
- Fetch all projects from SDGP website
- Save detailed project information to JSON
- Generate comprehensive project reports

### 2. Start the AI Chatbot
```bash
python enhanced_ai_chatbot.py
```

### 3. Example Chatbot Interactions

```
🤔 You: Tell me about AI projects
🤖 AI: I found 15 AI-related projects in the SDGP database...

🤔 You: What are the most popular technologies?
🤖 AI: Based on the analysis, the most popular technologies are...

🤔 You: details 78755d9c-f44b-4648-925b-8a2678d3be4c
🤖 AI: 🔍 DETAILED PROJECT ANALYSIS
     📋 Project ID: 78755d9c-f44b-4648-925b-8a2678d3be4c
     🔗 Project URL: https://www.sdgp.lk/project/78755d9c-f44b-4648-925b-8a2678d3be4c
     ...
```

## 📁 Project Structure

```
FYP_Data_Trace/
├── 📁 credentials/           # Google Cloud credentials (not in git)
├── 📁 output/               # Scraped data and reports
├── 📁 ai_cache/             # AI response cache
├── 📁 logs/                 # Application logs
├── 🤖 enhanced_ai_chatbot.py    # Main AI chatbot
├── 🕷️ sdgp_scraper.py          # Web scraper
├── 📊 data_analyzer.py          # Data analysis tools
├── 💾 ai_summary_manager.py     # AI caching system
├── ⚙️ config.py                 # Configuration management
├── 🚀 setup.py                  # Setup script
├── 📋 requirements.txt          # Python dependencies
├── 🔧 env.example              # Environment template
├── 📖 README.md                 # This file
├── 📚 AI_SETUP_GUIDE.md         # Detailed AI setup guide
└── 📄 .gitignore               # Git ignore rules
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account key | `credentials/service-account-key.json` |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | `gemini-api-project-462605` |
| `SCRAPER_DELAY` | Delay between requests (seconds) | `1.0` |
| `AI_MODEL_NAME` | AI model to use | `gemini-2.0-flash-exp` |
| `AI_CACHE_ENABLED` | Enable AI response caching | `true` |

### AI Chatbot Commands

- `stats` - Show cache statistics
- `clear cache` - Clear AI response cache
- `export` - Export all summaries
- `details [PROJECT_ID]` - Get detailed project information
- `quit` / `exit` - End the chat

## 🤖 AI Features

### Smart Project Analysis
- **Relevance Scoring**: Intelligent project matching based on keywords
- **Trend Analysis**: Identify patterns and popular technologies
- **Comparative Analysis**: Compare projects and highlight unique features

### Enhanced Responses
- **Direct Links**: Clickable links to official project pages
- **Project IDs**: Easy reference system for detailed information
- **Comprehensive Context**: Rich project details with AI-generated summaries

### Conversation Memory
- **Context Awareness**: Remembers previous interactions
- **Intelligent Follow-ups**: Builds on previous questions
- **Progressive Analysis**: Deeper insights based on conversation history

## 🔒 Security & Privacy

- ✅ **No Hardcoded Secrets**: All credentials use environment variables
- ✅ **Secure File Handling**: Credentials stored in dedicated directory
- ✅ **Git Ignore**: Sensitive files excluded from version control
- ✅ **API Rate Limiting**: Respectful scraping with configurable delays

## 🐛 Troubleshooting

### Common Issues

1. **"Google Cloud credentials not found"**
   - Run `python setup.py` to configure credentials
   - Ensure service account key is in `credentials/` folder

2. **"Vertex AI API not enabled"**
   - Enable Vertex AI API in Google Cloud Console
   - Ensure service account has `Vertex AI User` role

3. **"Configuration validation failed"**
   - Check `.env` file exists and is properly configured
   - Verify output directory is writable

### Getting Help

- 📖 Check [AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md) for detailed setup instructions
- 🔍 Review logs in `logs/` directory for error details
- 🐛 Check configuration with `python setup.py`

## 📊 Data Analysis

The scraper collects comprehensive project information:

- **Basic Info**: Title, status, year, domains, project types
- **Team Details**: Team size, member information
- **Technical Stack**: Technologies, frameworks, tools used
- **Project Details**: Problem statement, solution, features
- **AI Analysis**: Intelligent summaries and insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect the SDGP website's terms of service when scraping data.

## 🙏 Acknowledgments

- **SDGP Platform**: For providing the project data
- **Google Vertex AI**: For AI capabilities
- **Informatics Institute of Technology**: For the SDGP initiative

---

**Ready to explore SDGP projects?** Run `python setup.py` to get started! 🚀 