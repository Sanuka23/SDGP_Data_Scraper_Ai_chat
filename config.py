"""
Configuration management for SDGP Project Scraper.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional

# Base directory
BASE_DIR = Path(__file__).parent

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    'GOOGLE_APPLICATION_CREDENTIALS',
    str(BASE_DIR / 'credentials' / 'service-account-key.json')
)
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'gemini-api-project-462605')

# Scraping Configuration
SCRAPER_DELAY = float(os.getenv('SCRAPER_DELAY', '1.0'))
SCRAPER_TIMEOUT = int(os.getenv('SCRAPER_TIMEOUT', '30'))
SCRAPER_MAX_RETRIES = int(os.getenv('SCRAPER_MAX_RETRIES', '3'))

# AI Configuration
AI_MODEL_NAME = os.getenv('AI_MODEL_NAME', 'gemini-2.0-flash-exp')
AI_CACHE_ENABLED = os.getenv('AI_CACHE_ENABLED', 'true').lower() == 'true'
AI_CACHE_EXPIRY = int(os.getenv('AI_CACHE_EXPIRY', '86400'))  # 24 hours

# Output Configuration
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', str(BASE_DIR / 'output')))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# API Configuration
SDGP_API_BASE_URL = "https://www.sdgp.lk/api"
SDGP_PROJECTS_ENDPOINT = f"{SDGP_API_BASE_URL}/projects"
SDGP_PROJECT_DETAILS_ENDPOINT = f"{SDGP_API_BASE_URL}/projects"

# Headers for requests
DEFAULT_HEADERS = {
    'User-Agent': 'SDGP-Scraper/1.0 (Educational Project)',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
}

def validate_config() -> bool:
    """Validate that required configuration is present."""
    issues = []
    
    # Check if credentials file exists
    if not Path(GOOGLE_APPLICATION_CREDENTIALS).exists():
        issues.append(f"Google Cloud credentials file not found: {GOOGLE_APPLICATION_CREDENTIALS}")
    
    # Check if output directory is writable
    if not os.access(OUTPUT_DIR, os.W_OK):
        issues.append(f"Output directory is not writable: {OUTPUT_DIR}")
    
    if issues:
        print("❌ Configuration validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True

def get_credentials_path() -> Optional[str]:
    """Get the path to Google Cloud credentials file."""
    creds_path = Path(GOOGLE_APPLICATION_CREDENTIALS)
    
    # Check if the file exists
    if creds_path.exists():
        return str(creds_path)
    
    # Check common locations
    common_paths = [
        BASE_DIR / 'credentials' / 'service-account-key.json',
        BASE_DIR / 'gemini-api-project-462605-c948964a85ca.json',
        BASE_DIR / 'service-account-key.json',
    ]
    
    for path in common_paths:
        if path.exists():
            return str(path)
    
    return None 