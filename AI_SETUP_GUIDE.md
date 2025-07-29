# AI Setup Guide for SDGP Project Scraper

This guide will help you set up the AI-powered chatbot features for your SDGP (Software Development Group Project) scraper.

## 🎯 Overview

The AI features include:
- **AI-powered project summaries** - Automatically generate concise summaries for each project
- **Intelligent chatbot** - Ask questions about projects and get AI-powered responses
- **Caching system** - Store summaries for better performance
- **Conversation memory** - Remember previous interactions for context

## 🔧 Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Vertex AI API** enabled
3. **Service Account** with proper permissions
4. **Python 3.7+** with required dependencies

## 📋 Step-by-Step Setup

### 1. Google Cloud Project Setup

#### Create a New Project (if needed)
```bash
# Install Google Cloud CLI
# Visit: https://cloud.google.com/sdk/docs/install

# Initialize and create project
gcloud init
gcloud projects create your-project-id --name="Your Project Name"
gcloud config set project your-project-id
```

#### Enable Required APIs
```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable other required APIs
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable iam.googleapis.com
```

### 2. Service Account Setup

#### Create Service Account
```bash
# Create service account
gcloud iam service-accounts create sdgp-ai-bot \
    --display-name="SDGP AI Bot" \
    --description="Service account for SDGP (Software Development Group Project) AI chatbot"

# Get the service account email
SA_EMAIL=$(gcloud iam service-accounts list --filter="displayName:SDGP AI Bot" --format="value(email)")
```

#### Assign Permissions
```bash
# Grant Vertex AI User role
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/aiplatform.user"

# Grant Storage Object Viewer (if needed)
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.objectViewer"
```

#### Download Credentials
```bash
# Create and download key
gcloud iam service-accounts keys create gemini-api-project-462605-c948964a85ca.json \
    --iam-account=$SA_EMAIL
```

### 3. Python Dependencies

#### Install Required Packages
```bash
# Install Google Cloud dependencies
pip install google-cloud-aiplatform==1.38.1
pip install google-auth==2.23.4
pip install vertexai==0.0.1

# Or install all requirements
pip install -r requirements.txt
```

### 4. Environment Setup

#### Set Environment Variables (Optional)
```bash
# Set Google Cloud project
export GOOGLE_CLOUD_PROJECT=your-project-id

# Set credentials path
export GOOGLE_APPLICATION_CREDENTIALS=./gemini-api-project-462605-c948964a85ca.json
```

## 🚀 Usage

### 1. Basic AI Chatbot

```bash
# Run the basic AI chatbot
python ai_chatbot.py
```

**Features:**
- Loads project data automatically
- Generates AI summaries for each project
- Provides intelligent responses to questions
- Basic conversation capabilities

### 2. Enhanced AI Chatbot (Recommended)

```bash
# Run the enhanced AI chatbot
python enhanced_ai_chatbot.py
```

**Enhanced Features:**
- **Caching system** - Stores summaries for faster loading
- **Conversation memory** - Remembers previous interactions
- **Special commands** - Cache management and export features
- **Better performance** - Reuses cached summaries

### 3. Summary Manager (Standalone)

```bash
# Test the summary manager
python ai_summary_manager.py
```

## 💬 Chatbot Commands

### Basic Questions
- `"Tell me about AI projects"`
- `"What are the most popular technologies?"`
- `"Show me HealthTech projects"`
- `"What projects are deployed?"`
- `"Tell me about project trends"`

### Special Commands
- `stats` - Show cache statistics
- `clear cache` - Clear summary cache
- `export` - Export all summaries to JSON
- `quit` or `exit` - End the chat

## 🔍 Example Conversations

### Project Analysis
```
You: Tell me about AI projects
AI: Based on the SDGP project database, I found several AI-focused projects...

You: What technologies are most popular?
AI: Looking at the technology stack across all projects, the most commonly used technologies are...

You: Compare web and mobile projects
AI: Here's a comparison of web vs mobile projects in the SDGP database...
```

### Trend Analysis
```
You: What are the latest project trends?
AI: Analyzing the project data by year and domain, I can see several emerging trends...

You: Which domains are growing fastest?
AI: Based on the year-over-year analysis, the fastest growing domains are...
```

## 📊 Cache Management

### View Cache Statistics
```bash
# In the chatbot, type:
stats
```

### Clear Cache
```bash
# In the chatbot, type:
clear cache
```

### Export Summaries
```bash
# In the chatbot, type:
export
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
Error: Failed to initialize Vertex AI
```
**Solution:**
- Verify credentials file exists and is readable
- Check service account permissions
- Ensure Vertex AI API is enabled

#### 2. API Quota Exceeded
```
Error: Quota exceeded for quota group
```
**Solution:**
- Check Google Cloud billing
- Request quota increase if needed
- Use caching to reduce API calls

#### 3. Project Data Not Found
```
Error: No SDGP project data files found
```
**Solution:**
- Run the scraper first: `python run_scraper.py`
- Check output directory exists
- Verify JSON files are present

### Performance Optimization

#### 1. Use Caching
- The enhanced chatbot automatically caches summaries
- Subsequent runs will be much faster
- Cache persists between sessions

#### 2. Batch Processing
- Summaries are generated in batches
- Progress indicators show completion status
- Interrupt and resume capability

#### 3. Memory Management
- Conversation history limited to last 10 exchanges
- Automatic cleanup of old cache entries
- Efficient data structures

## 🔐 Security Considerations

### Credentials Management
- Keep service account key secure
- Don't commit credentials to version control
- Use environment variables in production
- Rotate keys regularly

### API Usage
- Monitor API usage and costs
- Set up billing alerts
- Use caching to minimize API calls
- Respect rate limits

## 📈 Advanced Features

### Custom Prompts
You can modify the summary generation prompts in the code:

```python
# In ai_chatbot.py or enhanced_ai_chatbot.py
summary_prompt = f"""
Create a concise, informative summary (2-3 sentences) for this SDGP project:
...
"""
```

### Model Selection
Change the AI model in the initialization:

```python
# Use different models
self.model = GenerativeModel("gemini-1.5-flash")  # Fast
self.model = GenerativeModel("gemini-1.5-pro")    # More capable
```

### Custom Context
Modify the context generation for different use cases:

```python
def _get_context_for_query(self, query: str) -> str:
    # Custom logic for context selection
    # ...
```

## 🎉 Next Steps

1. **Run the scraper** to get project data
2. **Test the basic chatbot** to verify setup
3. **Use the enhanced chatbot** for better performance
4. **Explore different questions** to understand capabilities
5. **Customize prompts** for your specific needs

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Check Google Cloud console for API status
4. Review logs for detailed error messages

Happy AI-powered project analysis! 🤖✨ 