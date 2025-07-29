#!/usr/bin/env python3
"""
SDGP Project Scraper
Scrapes all projects from https://www.sdgp.lk and stores them in a JSON file.
"""

import requests
import json
import time
import os
from typing import Dict, List, Optional
from tqdm import tqdm
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sdgp_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SDGPScraper:
    """Scraper for SDGP (Software Development Group Project) projects."""
    
    def __init__(self):
        self.base_url = "https://www.sdgp.lk"
        self.api_url = f"{self.base_url}/api/projects"
        self.session = requests.Session()
        
        # Set headers to mimic browser request
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.sdgp.lk/project',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=1, i'
        })
        
        self.projects_data = []
        self.total_projects = 0
        self.total_pages = 0
        
    def get_projects_page(self, page: int, limit: int = 9) -> Optional[Dict]:
        """
        Fetch a page of projects from the API.
        
        Args:
            page: Page number to fetch
            limit: Number of projects per page
            
        Returns:
            Dictionary containing projects data and metadata, or None if failed
        """
        try:
            url = f"{self.api_url}?page={page}&limit={limit}"
            logger.info(f"Fetching page {page} from {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched page {page}: {len(data.get('data', []))} projects")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page {page}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON for page {page}: {e}")
            return None
    
    def get_project_details(self, project_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific project.
        
        Args:
            project_id: The unique identifier of the project
            
        Returns:
            Dictionary containing detailed project information, or None if failed
        """
        try:
            url = f"{self.api_url}/{project_id}"
            logger.debug(f"Fetching details for project {project_id}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Successfully fetched details for project {project_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching details for project {project_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON for project {project_id}: {e}")
            return None
    
    def scrape_all_projects(self, delay: float = 1.0) -> List[Dict]:
        """
        Scrape all projects from the SDGP website.
        
        Args:
            delay: Delay between requests in seconds to be respectful to the server
            
        Returns:
            List of all projects with their details
        """
        logger.info("Starting to scrape all SDGP projects...")
        
        # Get the first page to understand pagination
        first_page = self.get_projects_page(1)
        if not first_page:
            logger.error("Failed to fetch first page. Exiting.")
            return []
        
        # Extract pagination metadata
        meta = first_page.get('meta', {})
        self.total_pages = meta.get('totalPages', 0)
        self.total_projects = meta.get('totalItems', 0)
        
        logger.info(f"Total projects: {self.total_projects}")
        logger.info(f"Total pages: {self.total_pages}")
        
        all_projects = []
        
        # Process all pages
        for page in tqdm(range(1, self.total_pages + 1), desc="Fetching project pages"):
            page_data = self.get_projects_page(page)
            if not page_data:
                logger.warning(f"Skipping page {page} due to fetch error")
                continue
            
            projects = page_data.get('data', [])
            all_projects.extend(projects)
            
            # Add delay between requests
            if page < self.total_pages:
                time.sleep(delay)
        
        logger.info(f"Successfully fetched {len(all_projects)} projects from {self.total_pages} pages")
        return all_projects
    
    def enrich_projects_with_details(self, projects: List[Dict], delay: float = 0.5) -> List[Dict]:
        """
        Enrich project list with detailed information for each project.
        
        Args:
            projects: List of basic project information
            delay: Delay between requests in seconds
            
        Returns:
            List of projects with detailed information
        """
        logger.info("Enriching projects with detailed information...")
        
        enriched_projects = []
        
        for project in tqdm(projects, desc="Fetching project details"):
            project_id = project.get('id')
            if not project_id:
                logger.warning(f"Project missing ID: {project}")
                enriched_projects.append(project)
                continue
            
            # Get detailed information
            details = self.get_project_details(project_id)
            if details:
                # Merge basic info with detailed info
                enriched_project = {
                    'basic_info': project,
                    'detailed_info': details
                }
                enriched_projects.append(enriched_project)
            else:
                # If details fetch failed, keep basic info
                enriched_projects.append({
                    'basic_info': project,
                    'detailed_info': None
                })
            
            # Add delay between requests
            time.sleep(delay)
        
        logger.info(f"Successfully enriched {len(enriched_projects)} projects")
        return enriched_projects
    
    def save_to_json(self, data: List[Dict], filename: str = None) -> str:
        """
        Save scraped data to a JSON file.
        
        Args:
            data: Data to save
            filename: Output filename (optional)
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sdgp_projects_{timestamp}.json"
        
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        filepath = os.path.join('output', filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving data to {filepath}: {e}")
            raise
    
    def run(self, include_details: bool = True, delay: float = 1.0) -> str:
        """
        Run the complete scraping process.
        
        Args:
            include_details: Whether to fetch detailed information for each project
            delay: Delay between requests in seconds
            
        Returns:
            Path to the saved JSON file
        """
        logger.info("Starting SDGP project scraper...")
        
        # Step 1: Scrape all projects
        projects = self.scrape_all_projects(delay=delay)
        
        if not projects:
            logger.error("No projects found. Exiting.")
            return None
        
        # Step 2: Enrich with details if requested
        if include_details:
            projects = self.enrich_projects_with_details(projects, delay=delay/2)
        
        # Step 3: Save to JSON
        filename = f"sdgp_projects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.save_to_json(projects, filename)
        
        logger.info(f"Scraping completed! Total projects: {len(projects)}")
        logger.info(f"Data saved to: {filepath}")
        
        return filepath


def main():
    """Main function to run the scraper."""
    print("SDGP Project Scraper")
    print("=" * 50)
    
    # Create scraper instance
    scraper = SDGPScraper()
    
    try:
        # Run the scraper
        output_file = scraper.run(include_details=True, delay=1.0)
        
        if output_file:
            print(f"\n✅ Scraping completed successfully!")
            print(f"📁 Output file: {output_file}")
            print(f"📊 Total projects scraped: {len(scraper.projects_data)}")
        else:
            print("\n❌ Scraping failed!")
            
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    main() 