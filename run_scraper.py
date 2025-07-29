#!/usr/bin/env python3
"""
Simple runner script for SDGP Scraper
Provides easy-to-use interface with different options.
"""

import argparse
import sys
from sdgp_scraper import SDGPScraper

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="SDGP Project Scraper - Scrape all projects from SDGP website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py                    # Run with default settings
  python run_scraper.py --basic-only       # Only fetch basic project info
  python run_scraper.py --fast             # Faster scraping (less delay)
  python run_scraper.py --delay 2.0        # Custom delay between requests
  python run_scraper.py --test             # Run test mode (small sample)
        """
    )
    
    parser.add_argument(
        '--basic-only',
        action='store_true',
        help='Only fetch basic project information (no detailed info)'
    )
    
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Faster scraping with reduced delays'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (small sample only)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Custom output filename'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("🚀 SDGP Project Scraper")
    print("=" * 50)
    
    # Create scraper instance
    scraper = SDGPScraper()
    
    try:
        # Configure scraping parameters
        include_details = not args.basic_only
        delay = args.delay
        
        if args.fast:
            delay = 0.5
            print("⚡ Fast mode enabled (reduced delays)")
        
        if args.basic_only:
            print("📋 Basic mode: Only fetching basic project information")
        else:
            print("📊 Full mode: Fetching detailed project information")
        
        print(f"⏱️  Delay between requests: {delay} seconds")
        
        if args.test:
            print("🧪 Test mode: Running with small sample")
            # Override for test mode
            def test_scrape_method(delay=1.0):
                """Test version that only scrapes first 2 pages."""
                first_page = scraper.get_projects_page(1)
                if not first_page:
                    return []
                
                all_projects = []
                projects = first_page.get('data', [])
                all_projects.extend(projects)
                
                # Get second page
                second_page = scraper.get_projects_page(2)
                if second_page:
                    projects = second_page.get('data', [])
                    all_projects.extend(projects)
                
                return all_projects
            
            original_method = scraper.scrape_all_projects
            scraper.scrape_all_projects = test_scrape_method
            
            # Run test
            projects = scraper.scrape_all_projects()
            
            if projects:
                if include_details:
                    projects = scraper.enrich_projects_with_details(projects, delay=delay/2)
                
                filename = args.output or "test_sdgp_projects.json"
                filepath = scraper.save_to_json(projects, filename)
                
                print(f"\n✅ Test completed successfully!")
                print(f"📁 Output file: {filepath}")
                print(f"📊 Projects scraped: {len(projects)}")
            
            # Restore original method
            scraper.scrape_all_projects = original_method
            
        else:
            # Run full scraping
            output_file = scraper.run(
                include_details=include_details,
                delay=delay
            )
            
            if output_file:
                print(f"\n✅ Scraping completed successfully!")
                print(f"📁 Output file: {output_file}")
            else:
                print("\n❌ Scraping failed!")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 