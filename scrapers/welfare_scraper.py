import requests
from bs4 import BeautifulSoup
import logging
import re
from datetime import datetime
from fake_useragent import UserAgent

class WelfareProgramsScraper:
    def __init__(self):
        self.welfare_sources = [
            {
                'name': 'Ministry of Social Justice',
                'url': 'https://socialjustice.gov.in/schemes',
                'type': 'social_welfare'
            }
        ]
    
    def scrape_welfare_programs(self):
        """Scrape welfare programs"""
        programs = []
        
        for source in self.welfare_sources:
            try:
                logging.info(f"Scraping welfare programs from {source['name']}...")
                
                headers = {'User-Agent': UserAgent().random}
                response = requests.get(source['url'], headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find program listings
                for link in soup.find_all('a', href=True)[:10]:
                    text = link.text
                    
                    if len(text) > 15 and ('pension' in text.lower() or 'welfare' in text.lower() or 'assistance' in text.lower()):
                        program = {
                            'title': text.strip(),
                            'description': 'Welfare program for eligible citizens',
                            'target_beneficiaries': self.extract_beneficiaries(text),
                            'category': self.determine_category(text),
                            'url': link['href'] if link['href'].startswith('http') else source['url'] + link['href'],
                            'source': source['name'],
                            'scraped_date': datetime.now().strftime('%Y-%m-%d')
                        }
                        
                        programs.append(program)
                
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error scraping {source['name']}: {str(e)}")
                continue
        
        return programs
    
    def extract_beneficiaries(self, text):
        """Extract target beneficiaries from text"""
        text_lower = text.lower()
        
        if 'elderly' in text_lower or 'senior' in text_lower or 'old age' in text_lower:
            return 'Senior Citizens'
        elif 'disabled' in text_lower or 'divyang' in text_lower:
            return 'Persons with Disabilities'
        elif 'women' in text_lower or 'female' in text_lower:
            return 'Women'
        elif 'child' in text_lower:
            return 'Children'
        else:
            return 'Eligible Citizens'
    
    def determine_category(self, text):
        """Determine program category"""
        text_lower = text.lower()
        
        if 'pension' in text_lower:
            return 'pension'
        elif 'health' in text_lower or 'medical' in text_lower:
            return 'health'
        elif 'education' in text_lower:
            return 'education'
        elif 'housing' in text_lower:
            return 'housing'
        else:
            return 'social_welfare'