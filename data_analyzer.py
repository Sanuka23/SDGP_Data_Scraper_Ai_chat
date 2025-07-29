#!/usr/bin/env python3
"""
SDGP Data Analyzer
Analyzes scraped project data and generates insights.
"""

import json
import os
from collections import Counter, defaultdict
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

class SDGPDataAnalyzer:
    """Analyzer for SDGP (Software Development Group Project) project data."""
    
    def __init__(self, data_file: str):
        """
        Initialize the analyzer with project data.
        
        Args:
            data_file: Path to the JSON file containing project data
        """
        self.data_file = data_file
        self.data = self.load_data()
        self.projects = self.extract_projects()
        
    def load_data(self) -> List[Dict]:
        """Load data from JSON file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            return []
    
    def extract_projects(self) -> List[Dict]:
        """Extract project information from the loaded data."""
        projects = []
        for item in self.data:
            if isinstance(item, dict):
                if 'basic_info' in item and 'detailed_info' in item:
                    # Enriched data format
                    project = {
                        'basic': item['basic_info'],
                        'detailed': item['detailed_info']
                    }
                else:
                    # Basic data format
                    project = {
                        'basic': item,
                        'detailed': None
                    }
                projects.append(project)
        return projects
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the projects."""
        stats = {
            'total_projects': len(self.projects),
            'projects_with_details': sum(1 for p in self.projects if p['detailed'] is not None),
            'projects_without_details': sum(1 for p in self.projects if p['detailed'] is None),
        }
        
        # Status distribution
        statuses = [p['basic'].get('status', 'Unknown') for p in self.projects]
        stats['status_distribution'] = dict(Counter(statuses))
        
        # Year distribution
        years = [p['basic'].get('year', 'Unknown') for p in self.projects]
        stats['year_distribution'] = dict(Counter(years))
        
        # Project types
        all_types = []
        for p in self.projects:
            types = p['basic'].get('projectTypes', [])
            all_types.extend(types)
        stats['project_types'] = dict(Counter(all_types))
        
        # Domains
        all_domains = []
        for p in self.projects:
            domains = p['basic'].get('domains', [])
            all_domains.extend(domains)
        stats['domains'] = dict(Counter(all_domains))
        
        return stats
    
    def analyze_tech_stack(self) -> Dict[str, Any]:
        """Analyze technology stack usage across projects."""
        tech_stack = defaultdict(int)
        projects_by_tech = defaultdict(list)
        
        for project in self.projects:
            if project['detailed'] and 'content' in project['detailed']:
                associations = project['detailed']['content'].get('associations', [])
                project_techs = []
                
                for assoc in associations:
                    if assoc.get('type') == 'PROJECT_TECH':
                        tech = assoc.get('techStack', 'Unknown')
                        tech_stack[tech] += 1
                        project_techs.append(tech)
                
                # Add project to tech categories
                for tech in project_techs:
                    projects_by_tech[tech].append({
                        'id': project['basic'].get('id'),
                        'title': project['basic'].get('title'),
                        'status': project['basic'].get('status')
                    })
        
        return {
            'tech_stack_usage': dict(tech_stack),
            'projects_by_tech': dict(projects_by_tech)
        }
    
    def analyze_team_sizes(self) -> Dict[str, Any]:
        """Analyze team sizes across projects."""
        team_sizes = []
        team_size_distribution = defaultdict(int)
        
        for project in self.projects:
            if project['detailed'] and 'content' in project['detailed']:
                team = project['detailed']['content'].get('team', [])
                team_size = len(team)
                team_sizes.append(team_size)
                team_size_distribution[team_size] += 1
        
        if team_sizes:
            return {
                'average_team_size': sum(team_sizes) / len(team_sizes),
                'min_team_size': min(team_sizes),
                'max_team_size': max(team_sizes),
                'team_size_distribution': dict(team_size_distribution),
                'total_teams_analyzed': len(team_sizes)
            }
        else:
            return {'error': 'No team data available'}
    
    def get_top_projects_by_domain(self, domain: str, limit: int = 10) -> List[Dict]:
        """Get top projects in a specific domain."""
        domain_projects = []
        
        for project in self.projects:
            domains = project['basic'].get('domains', [])
            if domain in domains:
                domain_projects.append({
                    'id': project['basic'].get('id'),
                    'title': project['basic'].get('title'),
                    'subtitle': project['basic'].get('subtitle'),
                    'status': project['basic'].get('status'),
                    'year': project['basic'].get('year'),
                    'domains': domains
                })
        
        # Sort by year (newer first) and then by status
        domain_projects.sort(key=lambda x: (x['year'], x['status']), reverse=True)
        return domain_projects[:limit]
    
    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report."""
        stats = self.get_basic_stats()
        tech_analysis = self.analyze_tech_stack()
        team_analysis = self.analyze_team_sizes()
        
        report = f"""
SDGP Projects Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data file: {self.data_file}

📊 BASIC STATISTICS
==================
Total Projects: {stats['total_projects']}
Projects with Details: {stats['projects_with_details']}
Projects without Details: {stats['projects_without_details']}

📈 STATUS DISTRIBUTION
=====================
"""
        for status, count in sorted(stats['status_distribution'].items(), key=lambda x: x[1], reverse=True):
            report += f"{status}: {count} projects\n"
        
        report += f"""
📅 YEAR DISTRIBUTION
===================
"""
        for year, count in sorted(stats['year_distribution'].items(), key=lambda x: x[1], reverse=True):
            report += f"{year}: {count} projects\n"
        
        report += f"""
🏷️  PROJECT TYPES
=================
"""
        for ptype, count in sorted(stats['project_types'].items(), key=lambda x: x[1], reverse=True):
            report += f"{ptype}: {count} projects\n"
        
        report += f"""
🌐 DOMAINS
==========
"""
        for domain, count in sorted(stats['domains'].items(), key=lambda x: x[1], reverse=True):
            report += f"{domain}: {count} projects\n"
        
        if 'tech_stack_usage' in tech_analysis:
            report += f"""
💻 TOP TECHNOLOGY STACKS
========================
"""
            for tech, count in sorted(tech_analysis['tech_stack_usage'].items(), key=lambda x: x[1], reverse=True)[:10]:
                report += f"{tech}: {count} projects\n"
        
        if 'average_team_size' in team_analysis:
            report += f"""
👥 TEAM ANALYSIS
================
Average Team Size: {team_analysis['average_team_size']:.1f} members
Min Team Size: {team_analysis['min_team_size']} members
Max Team Size: {team_analysis['max_team_size']} members
Total Teams Analyzed: {team_analysis['total_teams_analyzed']}

Team Size Distribution:
"""
            for size, count in sorted(team_analysis['team_size_distribution'].items()):
                report += f"  {size} members: {count} teams\n"
        
        return report
    
    def save_analysis_report(self, output_file: str = None) -> str:
        """Save the analysis report to a file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"sdgp_analysis_report_{timestamp}.txt"
        
        os.makedirs('output', exist_ok=True)
        filepath = os.path.join('output', output_file)
        
        report = self.generate_summary_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Analysis report saved to: {filepath}")
        return filepath


def main():
    """Main function to run the analyzer."""
    print("SDGP Data Analyzer")
    print("=" * 50)
    
    # Find the most recent data file
    output_dir = "output"
    if not os.path.exists(output_dir):
        print("❌ No output directory found. Please run the scraper first.")
        return
    
    data_files = [f for f in os.listdir(output_dir) if f.endswith('.json') and 'sdgp_projects' in f]
    if not data_files:
        print("❌ No SDGP project data files found. Please run the scraper first.")
        return
    
    # Use the most recent file
    latest_file = max(data_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
    data_file_path = os.path.join(output_dir, latest_file)
    
    print(f"📁 Analyzing data from: {data_file_path}")
    
    # Create analyzer and generate report
    analyzer = SDGPDataAnalyzer(data_file_path)
    report_file = analyzer.save_analysis_report()
    
    # Print summary to console
    stats = analyzer.get_basic_stats()
    print(f"\n📊 Quick Summary:")
    print(f"Total Projects: {stats['total_projects']}")
    print(f"Projects with Details: {stats['projects_with_details']}")
    
    if 'average_team_size' in analyzer.analyze_team_sizes():
        team_stats = analyzer.analyze_team_sizes()
        print(f"Average Team Size: {team_stats['average_team_size']:.1f} members")
    
    print(f"\n✅ Analysis completed! Report saved to: {report_file}")


if __name__ == "__main__":
    main() 