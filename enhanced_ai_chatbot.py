#!/usr/bin/env python3
"""
Enhanced SDGP AI Chatbot
An advanced CLI chatbot with caching, conversation memory, and intelligent project analysis.
"""

import json
import os
import sys
import time
import threading
from typing import Dict, List, Optional, Any
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel
import logging
from datetime import datetime
import re
from collections import deque
from dotenv import load_dotenv
from ai_summary_manager import AISummaryManager
from config import get_credentials_path, validate_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSDGPAIChatbot:
    """Enhanced AI-powered chatbot for SDGP (Software Development Group Project) analysis."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize the enhanced AI chatbot.
        
        Args:
            credentials_path: Path to Google Cloud service account credentials (optional)
        """
        # Get credentials path
        if credentials_path is None:
            credentials_path = get_credentials_path()
            if credentials_path is None:
                raise ValueError("Google Cloud credentials not found. Please run setup.py first.")
        
        self.credentials_path = credentials_path
        self.project_data = []
        self.summary_manager = AISummaryManager()
        self.chat_session = None
        self.model = None
        
        # Conversation memory
        self.conversation_history = deque(maxlen=10)  # Keep last 10 exchanges
        
        # Streaming state
        self.is_streaming = False
        self.typing_thread = None
        
        # Initialize Vertex AI
        self._initialize_vertex_ai()
        
        # Load project data
        self._load_project_data()
        
        # Generate project summaries (with caching)
        self._generate_project_summaries()
    
    def _initialize_vertex_ai(self):
        """Initialize Google Vertex AI with credentials."""
        try:
            # Load credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            # Initialize Vertex AI
            vertexai.init(
                project="gemini-api-project-462605",
                location="us-central1",
                credentials=credentials
            )
            
            # Initialize the model - using Gemini 2.0 Flash for better compatibility
            self.model = GenerativeModel("gemini-2.0-flash-exp")
            self.chat_session = None
            
            logger.info("✅ Vertex AI initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI: {e}")
            raise
    
    def _load_project_data(self):
        """Load SDGP project data from the most recent JSON file."""
        output_dir = "output"
        if not os.path.exists(output_dir):
            logger.error("❌ No output directory found. Please run the scraper first.")
            return
        
        # Find the most recent data file
        data_files = [f for f in os.listdir(output_dir) if f.endswith('.json') and 'sdgp_projects' in f]
        if not data_files:
            logger.error("❌ No SDGP project data files found. Please run the scraper first.")
            return
        
        latest_file = max(data_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
        data_file_path = os.path.join(output_dir, latest_file)
        
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                self.project_data = json.load(f)
            logger.info(f"✅ Loaded {len(self.project_data)} projects from {latest_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load project data: {e}")
            raise
    
    def _generate_project_summaries(self):
        """Generate AI summaries for each project with caching."""
        logger.info("🤖 Generating AI summaries for projects (with caching)...")
        
        new_summaries = 0
        cached_summaries = 0
        
        for i, project in enumerate(self.project_data):
            try:
                if 'basic_info' in project and 'detailed_info' in project:
                    project_id = project['basic_info'].get('id', f'project_{i}')
                    
                    # Check if summary exists in cache
                    cached_summary = self.summary_manager.get_summary(project_id, project)
                    
                    if cached_summary:
                        cached_summaries += 1
                        # Progress indicator for cached summaries
                        if (i + 1) % 20 == 0:
                            print(f"📝 Processed {i + 1}/{len(self.project_data)} projects (using cache)")
                    else:
                        # Generate new summary
                        summary = self._create_project_summary(project)
                        self.summary_manager.store_summary(project_id, project, summary)
                        new_summaries += 1
                        
                        # Progress indicator for new summaries
                        if (i + 1) % 10 == 0:
                            print(f"📝 Generated summaries for {i + 1}/{len(self.project_data)} projects")
                
            except Exception as e:
                logger.warning(f"⚠️  Failed to generate summary for project {i}: {e}")
                continue
        
        logger.info(f"✅ Summary generation completed!")
        logger.info(f"   📊 New summaries: {new_summaries}")
        logger.info(f"   📊 Cached summaries: {cached_summaries}")
    
    def _create_project_summary(self, project: Dict) -> str:
        """Create a concise AI summary for a project."""
        basic_info = project.get('basic_info', {})
        detailed_info = project.get('detailed_info', {})
        
        # Extract key information
        title = basic_info.get('title', 'Unknown')
        subtitle = basic_info.get('subtitle', '')
        status = basic_info.get('status', 'Unknown')
        domains = basic_info.get('domains', [])
        project_types = basic_info.get('projectTypes', [])
        year = basic_info.get('year', 'Unknown')
        
        # Extract detailed information
        problem_statement = ""
        solution = ""
        features = ""
        team_size = 0
        tech_stack = []
        
        if detailed_info and 'content' in detailed_info:
            content = detailed_info['content']
            
            # Project details
            if 'projectDetails' in content:
                details = content['projectDetails']
                problem_statement = details.get('problem_statement', '')
                solution = details.get('solution', '')
                features = details.get('features', '')
            
            # Team size
            if 'team' in content:
                team_size = len(content['team'])
            
            # Tech stack
            if 'associations' in content:
                for assoc in content['associations']:
                    if assoc.get('type') == 'PROJECT_TECH':
                        tech = assoc.get('techStack', '')
                        if tech:
                            tech_stack.append(tech)
        
        # Create enhanced summary prompt
        summary_prompt = f"""
        Create a detailed, comprehensive summary for this SDGP project. Include key details, technologies, and insights:

        PROJECT DETAILS:
        Title: {title}
        Description: {subtitle}
        Status: {status}
        Year: {year}
        Domains: {', '.join(domains)}
        Project Types: {', '.join(project_types)}
        
        TECHNICAL DETAILS:
        Problem Statement: {problem_statement}
        Solution Approach: {solution}
        Key Features: {features}
        Team Size: {team_size} members
        Technology Stack: {', '.join(tech_stack)}
        
        INSTRUCTIONS:
        1. Create a detailed 3-4 sentence summary explaining what this project does
        2. Highlight the main problem it solves and how
        3. Mention key technologies and innovative aspects
        4. Include relevant keywords for searchability (health, education, AI, IoT, etc.)
        5. Make it informative for both technical and non-technical readers
        6. Focus on the project's impact and value proposition
        
        Format the summary to be rich in detail and searchable keywords.
        """
        
        try:
            response = self.model.generate_content(summary_prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback summary
            return f"{title}: {subtitle} - A {', '.join(project_types)} project in {', '.join(domains)} domains."
    
    def _get_context_for_query(self, query: str) -> str:
        """Get relevant project context for a user query with enhanced search."""
        # Extract keywords from query
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Enhanced search with multiple strategies
        relevant_projects = []
        project_scores = {}
        
        for i, project in enumerate(self.project_data):
            if 'basic_info' not in project:
                continue
                
            basic_info = project['basic_info']
            project_id = basic_info.get('id', f'project_{i}')
            title = basic_info.get('title', '').lower()
            subtitle = basic_info.get('subtitle', '').lower()
            domains = [d.lower() for d in basic_info.get('domains', [])]
            project_types = [pt.lower() for pt in basic_info.get('projectTypes', [])]
            
            # Get detailed info for better matching
            detailed_info = project.get('detailed_info', {})
            content = detailed_info.get('content', {})
            project_details = content.get('projectDetails', {})
            problem = project_details.get('problem_statement', '').lower()
            solution = project_details.get('solution', '').lower()
            features = project_details.get('features', '').lower()
            
            # Calculate relevance score
            score = 0
            
            # Direct keyword matches
            for word in query_words:
                if word in title:
                    score += 10
                if word in subtitle:
                    score += 8
                if word in problem:
                    score += 6
                if word in solution:
                    score += 6
                if word in features:
                    score += 4
                if any(word in domain for domain in domains):
                    score += 7
                if any(word in pt for pt in project_types):
                    score += 7
            
            # Domain-specific searches
            if 'health' in query_lower or 'medical' in query_lower:
                if any(domain in ['healthcare', 'medical', 'health'] for domain in domains):
                    score += 15
                if 'health' in problem or 'medical' in problem:
                    score += 10
                    
            if 'education' in query_lower or 'edtech' in query_lower:
                if any(domain in ['education', 'edtech', 'learning'] for domain in domains):
                    score += 15
                if 'education' in problem or 'learning' in problem:
                    score += 10
                    
            if 'ai' in query_lower or 'artificial intelligence' in query_lower:
                if any(domain in ['ai', 'artificial intelligence', 'machine learning'] for domain in domains):
                    score += 15
                if 'ai' in problem or 'intelligence' in problem:
                    score += 10
            
            # Add to relevant projects if score > 0
            if score > 0:
                project_scores[project_id] = (score, project)
        
        # Sort by relevance score
        sorted_projects = sorted(project_scores.items(), key=lambda x: x[1][0], reverse=True)
        relevant_projects = [project for project_id, (score, project) in sorted_projects[:10]]  # Top 10 most relevant
        
        # If no specific matches, return comprehensive overview
        if not relevant_projects:
            return self._get_comprehensive_overview(query_lower)
        
        # Build detailed context from relevant projects with enhanced information
        context = f"Found {len(relevant_projects)} relevant projects for '{query}':\n\n"
        
        for i, project in enumerate(relevant_projects):
            basic_info = project['basic_info']
            project_id = basic_info.get('id', f'project_{i}')
            
            # Get enhanced summary from cache
            summary = self.summary_manager.get_summary(project_id, project)
            if not summary:
                summary = self._create_project_summary(project)  # Generate on-the-fly if needed
            
            # Extract additional details
            detailed_info = project.get('detailed_info', {})
            content = detailed_info.get('content', {})
            project_details = content.get('projectDetails', {})
            
            # Get team information
            team_size = len(content.get('team', [])) if 'team' in content else 0
            
            # Get tech stack
            tech_stack = []
            if 'associations' in content:
                for assoc in content['associations']:
                    if assoc.get('type') == 'PROJECT_TECH':
                        tech = assoc.get('techStack', '')
                        if tech:
                            tech_stack.append(tech)
            
            context += f"📋 PROJECT ID: {project_id}\n"
            context += f"🔗 Project URL: https://www.sdgp.lk/project/{project_id}\n"
            context += f"Title: {basic_info.get('title', 'Unknown')}\n"
            context += f"Status: {basic_info.get('status', 'Unknown')}\n"
            context += f"Year: {basic_info.get('year', 'Unknown')}\n"
            context += f"Domains: {', '.join(basic_info.get('domains', []))}\n"
            context += f"Project Types: {', '.join(basic_info.get('projectTypes', []))}\n"
            context += f"Team Size: {team_size} members\n"
            context += f"Tech Stack: {', '.join(tech_stack) if tech_stack else 'Not specified'}\n"
            context += f"Problem: {project_details.get('problem_statement', 'Not specified')[:150]}...\n"
            context += f"Solution: {project_details.get('solution', 'Not specified')[:150]}...\n"
            context += f"Features: {project_details.get('features', 'Not specified')[:150]}...\n"
            context += f"AI Summary: {summary}\n\n"
        
        return context
    
    def _get_comprehensive_overview(self, query: str) -> str:
        """Get comprehensive overview when no specific matches found."""
        # Analyze all projects for related content
        related_projects = []
        domain_stats = {}
        
        for project in self.project_data:
            if 'basic_info' not in project:
                continue
                
            basic_info = project['basic_info']
            domains = basic_info.get('domains', [])
            
            # Count domains
            for domain in domains:
                domain_stats[domain] = domain_stats.get(domain, 0) + 1
            
            # Check for any related content
            detailed_info = project.get('detailed_info', {})
            content = detailed_info.get('content', {})
            project_details = content.get('projectDetails', {})
            
            problem = project_details.get('problem_statement', '').lower()
            solution = project_details.get('solution', '').lower()
            
            # Look for any related keywords
            if any(word in problem or word in solution for word in query.split()):
                related_projects.append(project)
        
        context = f"""
        COMPREHENSIVE SDGP (SOFTWARE DEVELOPMENT GROUP PROJECT) ANALYSIS:
        
        📊 Database Overview:
        - Total Projects: {len(self.project_data)}
        - Projects with any relevance to '{query}': {len(related_projects)}
        
        🏷️ Domain Distribution:
        {chr(10).join([f"- {domain}: {count} projects" for domain, count in sorted(domain_stats.items(), key=lambda x: x[1], reverse=True)[:8]])}
        
        💡 Related Projects Found:
        """
        
        if related_projects:
            for i, project in enumerate(related_projects[:5]):
                basic_info = project['basic_info']
                project_id = basic_info.get('id', 'unknown')
                context += f"\n{i+1}. {basic_info.get('title', 'Unknown')} ({', '.join(basic_info.get('domains', []))}) - https://www.sdgp.lk/project/{project_id}"
        else:
            context += "\nNo directly related projects found, but here are some interesting projects from different domains:"
            # Show some diverse projects
            for i, project in enumerate(self.project_data[:5]):
                if 'basic_info' in project:
                    basic_info = project['basic_info']
                    project_id = basic_info.get('id', 'unknown')
                    context += f"\n{i+1}. {basic_info.get('title', 'Unknown')} ({', '.join(basic_info.get('domains', []))}) - https://www.sdgp.lk/project/{project_id}"
        
        return context
    
    def _get_general_context(self) -> str:
        """Get general context about all projects."""
        total_projects = len(self.project_data)
        
        # Calculate statistics
        status_counts = {}
        domain_counts = {}
        year_counts = {}
        
        for project in self.project_data:
            if 'basic_info' in project:
                basic_info = project['basic_info']
                
                # Status counts
                status = basic_info.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Domain counts
                for domain in basic_info.get('domains', []):
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
                
                # Year counts
                year = basic_info.get('year', 'Unknown')
                year_counts[year] = year_counts.get(year, 0) + 1
        
        context = f"""
        SDGP Project Database Overview:
        - Total Projects: {total_projects}
        
        Status Distribution:
        {chr(10).join([f"- {status}: {count}" for status, count in status_counts.items()])}
        
        Top Domains:
        {chr(10).join([f"- {domain}: {count}" for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]])}
        
        Year Distribution:
        {chr(10).join([f"- {year}: {count}" for year, count in sorted(year_counts.items(), reverse=True)])}
        """
        
        return context
    
    def _add_to_conversation_history(self, user_input: str, ai_response: str):
        """Add exchange to conversation history."""
        self.conversation_history.append({
            'user': user_input,
            'ai': ai_response,
            'timestamp': datetime.now().isoformat()
        })
    
    def _get_conversation_context(self) -> str:
        """Get recent conversation context."""
        if not self.conversation_history:
            return ""
        
        context = "Recent conversation:\n"
        for i, exchange in enumerate(list(self.conversation_history)[-3:]):  # Last 3 exchanges
            context += f"User: {exchange['user']}\n"
            context += f"AI: {exchange['ai'][:100]}...\n\n"
        
        return context

    def _show_typing_indicator(self, stop_event):
        """Show typing indicator while AI is thinking."""
        indicators = ["🤔", "💭", "🧠", "💡", "✨"]
        i = 0
        while not stop_event.is_set():
            print(f"\r🤖 AI is thinking {indicators[i]}", end="", flush=True)
            time.sleep(0.5)
            i = (i + 1) % len(indicators)
        print("\r", end="", flush=True)  # Clear the line
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and return AI response with enhanced features.
        
        Args:
            user_input: User's question or query
            
        Returns:
            AI-generated response
        """
        try:
            # Check for special commands first
            user_input_lower = user_input.lower().strip()
            
            # Handle project ID requests
            if user_input_lower.startswith('details ') or user_input_lower.startswith('project '):
                # Extract project ID from input
                words = user_input_lower.split()
                for word in words:
                    if word.isdigit() or (word.startswith('project_') and len(word) > 8):
                        project_id = word
                        detailed_info = self.get_detailed_project_info(project_id)
                        if detailed_info:
                            return detailed_info
                        else:
                            return f"❌ Project ID '{project_id}' not found. Please check the project ID and try again."
            
            # Handle special commands
            if user_input_lower == 'stats':
                stats = self.get_cache_stats()
                return f"""
📊 **Cache Statistics:**
- Total summaries: {stats.get('total_summaries', 0)}
- Cache size: {stats.get('cache_size_mb', 0):.2f} MB
- Projects processed: {len(self.project_data)}
"""
            
            if user_input_lower == 'clear cache':
                self.clear_cache()
                return "✅ Cache cleared successfully! All summaries will be regenerated on next run."
            
            if user_input_lower == 'export':
                export_data = self.export_summaries()
                return f"📤 Export data available. Summary: {export_data[:200]}..."
            
            # Get relevant context
            context = self._get_context_for_query(user_input)
            conversation_context = self._get_conversation_context()
            
            # Create the enhanced full prompt with emotional intelligence and detailed guidance
            full_prompt = f"""
            You are an expert AI assistant specialized in analyzing SDGP (Software Development Group Project) projects. 
            Act as a knowledgeable, empathetic guide who helps users understand and explore these projects effectively.
            
            CONTEXT DATA:
            {context}
            
            CONVERSATION HISTORY:
            {conversation_context}
            
            USER QUESTION: {user_input}
            
            RESPONSE GUIDELINES - Create a comprehensive, emotionally intelligent response:
            
            1. **📊 START WITH OVERVIEW**: Begin with a warm, engaging summary of what you found
            2. **🔍 DETAILED ANALYSIS**: Provide rich insights about the projects, technologies, and trends
            3. **📋 PROJECT IDENTIFICATION**: For each relevant project, include:
               - Project ID (for reference)
               - 🔗 Direct link to project page: https://www.sdgp.lk/project/[ACTUAL_PROJECT_ID]
               - Full project title
               - Key domains and technologies
               - Brief but compelling description
            4. **💡 INSIGHTS & TRENDS**: Share patterns, innovations, and interesting observations
            5. **🎯 ACTIONABLE STEPS**: Provide clear next steps for users who want to:
               - Get more details about specific projects
               - Explore similar projects
               - Understand the technology stack
               - Learn about project development stages
               - Visit official project pages
            6. **🔗 REFERENCE SYSTEM**: Use project IDs like [PROJECT_ID:123] for easy reference
            7. **📈 COMPARATIVE ANALYSIS**: When relevant, compare projects and highlight unique features
            8. **🌟 HIGHLIGHT INNOVATIONS**: Emphasize cutting-edge technologies and novel approaches
            9. **🌐 DIRECT LINKS**: Include clickable links to official SDGP project pages in the project identification section (no separate section needed)
            
            EMOTIONAL INTELLIGENCE ELEMENTS:
            - Be enthusiastic about the innovative projects you discover
            - Show genuine interest in helping users explore the data
            - Use encouraging language that makes users want to learn more
            - Acknowledge the impressive scope and diversity of the SDGP projects
            
            STRUCTURE YOUR RESPONSE WITH:
            - 📊 **Overview & Statistics**
            - 🔍 **Detailed Project Analysis** (with Project IDs and Direct Links)
            - 💡 **Key Insights & Trends**
            - 🎯 **Next Steps & Recommendations**
            - 🔗 **How to Get More Details**
            
            IMPORTANT: Always mention that users can get detailed information about any project by typing "details [PROJECT_ID]" or "project [PROJECT_ID]"
            
            Remember: You have access to 209 SDGP projects with detailed summaries. Make users excited about exploring this rich ecosystem of software development innovation!
            """
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            ai_response = response.text
            
            # Add to conversation history
            self._add_to_conversation_history(user_input, ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"

    def chat_streaming(self, user_input: str, callback=None):
        """
        Generate a streaming response to user input using AI.
        
        Args:
            user_input: The user's question or input
            callback: Optional callback function to handle streaming chunks
            
        Yields:
            Streaming response chunks
        """
        try:
            # Check for special commands first (non-streaming for these)
            user_input_lower = user_input.lower().strip()
            
            # Handle project ID requests
            if user_input_lower.startswith('details ') or user_input_lower.startswith('project '):
                words = user_input_lower.split()
                for word in words:
                    if word.isdigit() or (word.startswith('project_') and len(word) > 8):
                        project_id = word
                        detailed_info = self.get_detailed_project_info(project_id)
                        if detailed_info:
                            yield detailed_info
                        else:
                            yield f"❌ Project ID '{project_id}' not found. Please check the project ID and try again."
                        return
            
            # Handle special commands
            if user_input_lower == 'stats':
                stats = self.get_cache_stats()
                response = f"""
📊 **Cache Statistics:**
- Total summaries: {stats.get('total_summaries', 0)}
- Cache size: {stats.get('cache_size_mb', 0):.2f} MB
- Projects processed: {len(self.project_data)}
"""
                yield response
                return
            
            if user_input_lower == 'clear cache':
                self.clear_cache()
                yield "✅ Cache cleared successfully! All summaries will be regenerated on next run."
                return
            
            if user_input_lower == 'export':
                export_data = self.export_summaries()
                yield f"📤 Export data available. Summary: {export_data[:200]}..."
                return
            
            # Get relevant context
            context = self._get_context_for_query(user_input)
            conversation_context = self._get_conversation_context()
            
            # Create the enhanced full prompt
            full_prompt = f"""
            You are an expert AI assistant specialized in analyzing SDGP (Software Development Group Project) projects. 
            Act as a knowledgeable, empathetic guide who helps users understand and explore these projects effectively.
            
            CONTEXT DATA:
            {context}
            
            CONVERSATION HISTORY:
            {conversation_context}
            
            USER QUESTION: {user_input}
            
            RESPONSE GUIDELINES - Create a comprehensive, emotionally intelligent response:
            
            1. **📊 START WITH OVERVIEW**: Begin with a warm, engaging summary of what you found
            2. **🔍 DETAILED ANALYSIS**: Provide rich insights about the projects, technologies, and trends
            3. **📋 PROJECT IDENTIFICATION**: For each relevant project, include:
               - Project ID (for reference)
               - 🔗 Direct link to project page: https://www.sdgp.lk/project/[ACTUAL_PROJECT_ID]
               - Full project title
               - Key domains and technologies
               - Brief but compelling description
            4. **💡 INSIGHTS & TRENDS**: Share patterns, innovations, and interesting observations
            5. **🎯 ACTIONABLE STEPS**: Provide clear next steps for users who want to:
               - Get more details about specific projects
               - Explore similar projects
               - Understand the technology stack
               - Learn about project development stages
               - Visit official project pages
            6. **🔗 REFERENCE SYSTEM**: Use project IDs like [PROJECT_ID:123] for easy reference
            7. **📈 COMPARATIVE ANALYSIS**: When relevant, compare projects and highlight unique features
            8. **🌟 HIGHLIGHT INNOVATIONS**: Emphasize cutting-edge technologies and novel approaches
            9. **🌐 DIRECT LINKS**: Include clickable links to official SDGP project pages in the project identification section (no separate section needed)
            
            EMOTIONAL INTELLIGENCE ELEMENTS:
            - Be enthusiastic about the innovative projects you discover
            - Show genuine interest in helping users explore the data
            - Use encouraging language that makes users want to learn more
            - Acknowledge the impressive scope and diversity of the SDGP projects
            
            STRUCTURE YOUR RESPONSE WITH:
            - 📊 **Overview & Statistics**
            - 🔍 **Detailed Project Analysis** (with Project IDs and Direct Links)
            - 💡 **Key Insights & Trends**
            - 🎯 **Next Steps & Recommendations**
            - 🔗 **How to Get More Details**
            
            IMPORTANT: Always mention that users can get detailed information about any project by typing "details [PROJECT_ID]" or "project [PROJECT_ID]"
            
            Remember: You have access to 209 SDGP projects with detailed summaries. Make users excited about exploring this rich ecosystem of software development innovation!
            """
            
            # Start typing indicator
            stop_event = threading.Event()
            typing_thread = threading.Thread(target=self._show_typing_indicator, args=(stop_event,))
            typing_thread.daemon = True
            typing_thread.start()
            
            try:
                # Generate streaming response
                response_stream = self.model.generate_content(full_prompt, stream=True)
                
                full_response = ""
                first_chunk = True
                
                # Stream the response
                for chunk in response_stream:
                    if hasattr(chunk, 'text') and chunk.text:
                        # Stop typing indicator on first chunk
                        if first_chunk:
                            stop_event.set()
                            typing_thread.join(timeout=1)
                            first_chunk = False
                        
                        chunk_text = chunk.text
                        full_response += chunk_text
                        
                        # Yield the chunk
                        yield chunk_text
                        
                        # Call callback if provided
                        if callback:
                            callback(chunk_text)
                
                # Ensure typing indicator is stopped
                stop_event.set()
                typing_thread.join(timeout=1)
                
            except Exception as e:
                # Ensure typing indicator is stopped on error
                stop_event.set()
                typing_thread.join(timeout=1)
                raise e
            
            # Update conversation history with the full response
            self._add_to_conversation_history(user_input, full_response)
            
        except Exception as e:
            logger.error(f"❌ Error generating streaming response: {e}")
            error_msg = f"I apologize, but I encountered an error while processing your request: {e}"
            yield error_msg
            if callback:
                callback(error_msg)
    
    def get_project_by_name(self, project_name: str) -> Optional[Dict]:
        """Find a specific project by name."""
        project_name_lower = project_name.lower()
        
        for project in self.project_data:
            if 'basic_info' in project:
                title = project['basic_info'].get('title', '').lower()
                if project_name_lower in title or title in project_name_lower:
                    return project
        
        return None
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """Find a specific project by ID."""
        for project in self.project_data:
            if 'basic_info' in project:
                if project['basic_info'].get('id') == project_id:
                    return project
        return None
    
    def get_detailed_project_info(self, project_id: str) -> Optional[str]:
        """Get detailed information about a specific project."""
        project = self.get_project_by_id(project_id)
        if not project:
            return f"❌ Project with ID '{project_id}' not found."
        
        basic_info = project['basic_info']
        detailed_info = project.get('detailed_info', {})
        content = detailed_info.get('content', {})
        project_details = content.get('projectDetails', {})
        
        # Get team information
        team = content.get('team', [])
        team_size = len(team)
        
        # Get tech stack
        tech_stack = []
        if 'associations' in content:
            for assoc in content['associations']:
                if assoc.get('type') == 'PROJECT_TECH':
                    tech = assoc.get('techStack', '')
                    if tech:
                        tech_stack.append(tech)
        
        # Get summary
        summary = self.summary_manager.get_summary(project_id, project)
        if not summary:
            summary = self._create_project_summary(project)
        
        detailed_info = f"""
🔍 **DETAILED PROJECT ANALYSIS**

📋 **Basic Information:**
- **Project ID:** {project_id}
- **🔗 Project URL:** https://www.sdgp.lk/project/{project_id}
- **Title:** {basic_info.get('title', 'Unknown')}
- **Status:** {basic_info.get('status', 'Unknown')}
- **Year:** {basic_info.get('year', 'Unknown')}
- **Domains:** {', '.join(basic_info.get('domains', []))}
- **Project Types:** {', '.join(basic_info.get('projectTypes', []))}

👥 **Team Information:**
- **Team Size:** {team_size} members
- **Team Members:** {', '.join([member.get('name', 'Unknown') for member in team]) if team else 'Not specified'}

🛠️ **Technical Details:**
- **Technology Stack:** {', '.join(tech_stack) if tech_stack else 'Not specified'}

📝 **Project Details:**
- **Problem Statement:** {project_details.get('problem_statement', 'Not specified')}
- **Solution Approach:** {project_details.get('solution', 'Not specified')}
- **Key Features:** {project_details.get('features', 'Not specified')}

🤖 **AI Analysis:**
{summary}

💡 **Key Insights:**
- This project addresses: {project_details.get('problem_statement', 'Not specified')[:100]}...
- Innovative aspects: {', '.join(basic_info.get('domains', []))} integration
- Target impact: {basic_info.get('status', 'Unknown')} stage development

🌐 **Visit Project:** [View on SDGP Platform](https://www.sdgp.lk/project/{project_id})
"""
        
        return detailed_info
    
    def search_projects(self, query: str) -> List[Dict]:
        """Search projects based on query."""
        query_lower = query.lower()
        results = []
        
        for project in self.project_data:
            if 'basic_info' not in project:
                continue
                
            basic_info = project['basic_info']
            title = basic_info.get('title', '').lower()
            subtitle = basic_info.get('subtitle', '').lower()
            domains = [d.lower() for d in basic_info.get('domains', [])]
            
            if (query_lower in title or 
                query_lower in subtitle or 
                any(query_lower in domain for domain in domains)):
                results.append(project)
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return self.summary_manager.get_summary_stats()
    
    def clear_cache(self):
        """Clear the summary cache."""
        self.summary_manager.clear_cache()
    
    def export_summaries(self) -> str:
        """Export all summaries."""
        return self.summary_manager.export_summaries()


def main():
    """Main function for the enhanced CLI chatbot."""
    print("🤖 Enhanced SDGP (Software Development Group Project) AI Chatbot")
    print("=" * 50)
    print("Loading project data and initializing AI...")
    
    # Validate configuration
    if not validate_config():
        print("\n❌ Configuration validation failed.")
        print("Please run 'python setup.py' to configure the project.")
        sys.exit(1)
    
    try:
        # Initialize chatbot
        chatbot = EnhancedSDGPAIChatbot()
        
        # Show cache stats
        cache_stats = chatbot.get_cache_stats()
        print(f"📊 Cache Statistics:")
        print(f"  Total summaries: {cache_stats['total_summaries']}")
        print(f"  Cache size: {cache_stats['cache_size_mb']} MB")
        
        print("\n✅ Enhanced AI Chatbot ready!")
        print("\n💡 You can ask questions like:")
        print("- 'Tell me about AI projects'")
        print("- 'What are the most popular technologies?'")
        print("- 'Show me HealthTech projects'")
        print("- 'What projects are deployed?'")
        print("- 'Tell me about project trends'")
        print("- 'Compare different project types'")
        print("- 'What are the latest projects?'")
        print()
        print("🔍 **Enhanced Features:**")
        print("- Get detailed project info: 'details [PROJECT_ID]' or 'project [PROJECT_ID]'")
        print("- Example: 'details 123' or 'project project_45'")
        print("- Direct links to official SDGP project pages included in all responses")
        print()
        print("📊 Special commands:")
        print("- 'stats' - Show cache statistics")
        print("- 'clear cache' - Clear summary cache")
        print("- 'export' - Export summaries")
        print("- 'quit' or 'exit' - End the chat")
        print()
        print("🎯 **How to use this enhanced chatbot:**")
        print("1. Ask general questions about projects, technologies, or trends")
        print("2. Look for Project IDs and direct links in the responses")
        print("3. Use 'details [PROJECT_ID]' to get comprehensive project information")
        print("4. Click on project links to visit official SDGP project pages")
        print("5. Explore related projects and technologies")
        print("6. Use the insights to understand the SDGP (Software Development Group Project) ecosystem better")
        print("-" * 50)
        
        # Chat loop
        while True:
            try:
                user_input = input("\n🤔 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Thanks for using Enhanced SDGP AI Chatbot!")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'stats':
                    stats = chatbot.get_cache_stats()
                    print(f"\n📊 Cache Statistics:")
                    print(f"  Total summaries: {stats['total_summaries']}")
                    print(f"  Cache size: {stats['cache_size_mb']} MB")
                    if stats['creation_dates']:
                        print(f"  Creation dates: {stats['creation_dates']}")
                    continue
                
                elif user_input.lower() == 'clear cache':
                    chatbot.clear_cache()
                    print("✅ Cache cleared!")
                    continue
                
                elif user_input.lower() == 'export':
                    try:
                        export_file = chatbot.export_summaries()
                        print(f"✅ Summaries exported to: {export_file}")
                    except Exception as e:
                        print(f"❌ Export failed: {e}")
                    continue
                
                print("🤖 AI: ", end="", flush=True)
                
                # Use streaming response for better user experience
                try:
                    for chunk in chatbot.chat_streaming(user_input):
                        print(chunk, end="", flush=True)
                    print()  # New line after response
                except Exception as e:
                    print(f"\n❌ Error during streaming: {e}")
                    # Fallback to non-streaming response
                    response = chatbot.chat(user_input)
                    print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for using Enhanced SDGP AI Chatbot!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("Please make sure:")
        print("1. You have run the scraper first (python run_scraper.py)")
        print("2. Your Google Cloud credentials file is in the correct location")
        print("3. You have enabled Vertex AI API in your Google Cloud project")
        sys.exit(1)


if __name__ == "__main__":
    main() 