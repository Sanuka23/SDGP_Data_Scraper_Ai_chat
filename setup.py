#!/usr/bin/env python3
"""
Setup script for SDGP Project Scraper.
Helps users configure the project and set up their environment.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional

def print_banner():
    """Print the setup banner."""
    print("=" * 60)
    print("🤖 SDGP Project Scraper Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
        print("✅ Dependencies installed successfully")
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def setup_credentials():
    """Set up Google Cloud credentials."""
    print("\n🔐 Setting up Google Cloud credentials...")
    
    # Check if credentials already exist
    creds_path = Path("credentials/service-account-key.json")
    if creds_path.exists():
        print("✅ Credentials file already exists")
        return str(creds_path)
    
    # Create credentials directory
    creds_dir = Path("credentials")
    creds_dir.mkdir(exist_ok=True)
    
    # Check for existing service account key
    existing_keys = list(Path(".").glob("*-service-account*.json")) + \
                   list(Path(".").glob("gemini-api-project-*.json"))
    
    if existing_keys:
        print("📁 Found existing service account key:")
        for key in existing_keys:
            print(f"   - {key}")
        
        choice = input("\nWould you like to move one of these to the credentials folder? (y/n): ").lower()
        if choice == 'y':
            for i, key in enumerate(existing_keys, 1):
                print(f"   {i}. {key}")
            
            try:
                selection = int(input("Select a file (number): ")) - 1
                if 0 <= selection < len(existing_keys):
                    selected_key = existing_keys[selection]
                    shutil.move(str(selected_key), str(creds_path))
                    print(f"✅ Moved {selected_key} to {creds_path}")
                    return str(creds_path)
            except (ValueError, IndexError):
                print("❌ Invalid selection")
    
    print("\n📋 To set up Google Cloud credentials:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable Vertex AI API")
    print("4. Create a service account with 'Vertex AI User' role")
    print("5. Download the JSON key file")
    print("6. Place it in the 'credentials/' folder as 'service-account-key.json'")
    print("\n📖 See AI_SETUP_GUIDE.md for detailed instructions")
    
    return None

def create_env_file():
    """Create .env file from template."""
    print("\n⚙️ Setting up environment configuration...")
    
    if Path(".env").exists():
        print("✅ .env file already exists")
        return True
    
    if Path("env.example").exists():
        shutil.copy("env.example", ".env")
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your configuration")
        return True
    
    print("❌ env.example template not found")
    return False

def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")
    
    directories = ["output", "credentials", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")

def validate_setup():
    """Validate the setup."""
    print("\n🔍 Validating setup...")
    
    issues = []
    
    # Check credentials
    creds_path = Path("credentials/service-account-key.json")
    if not creds_path.exists():
        issues.append("Google Cloud credentials not found")
    
    # Check .env file
    if not Path(".env").exists():
        issues.append(".env file not found")
    
    # Check output directory
    if not Path("output").exists():
        issues.append("Output directory not found")
    
    if issues:
        print("❌ Setup validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ Setup validation passed")
    return True

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Setup credentials
    creds_path = setup_credentials()
    
    # Create .env file
    create_env_file()
    
    # Validate setup
    if validate_setup():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit .env file with your configuration")
        print("2. Add your Google Cloud service account key to credentials/")
        print("3. Run: python run_scraper.py")
        print("4. Run: python enhanced_ai_chatbot.py")
        print("\n📖 For detailed instructions, see README.md and AI_SETUP_GUIDE.md")
    else:
        print("\n⚠️ Setup completed with issues. Please resolve them before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main() 