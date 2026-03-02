import requests
from bs4 import BeautifulSoup
import logging
import time
from datetime import datetime
from fake_useragent import UserAgent

class GovernmentSchemesScraper:
    def __init__(self):
        self.scheme_sources = [
            {
                'name': 'MyScheme',
                'url': 'https://www.myscheme.gov.in/search/all-schemes',
                'type': 'central'
            },
            {
                'name': 'PM India',
                'url': 'https://www.pmindia.gov.in/en/schemes/',
                'type': 'central'
            }
        ]
    
    def scrape_all_schemes(self):
        """Scrape all government schemes"""
        all_schemes = []
        
        for source in self.scheme_sources:
            try:
                logging.info(f"Scraping schemes from {source['name']}...")
                
                headers = {'User-Agent': UserAgent().random}
                response = requests.get(source['url'], headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find scheme listings
                for link in soup.find_all('a', href=True)[:15]:
                    text = link.text
                    
                    if len(text) > 15 and 'scheme' in text.lower():
                        scheme = {
                            'title': text.strip(),
                            'description': 'Government scheme for citizens',
                            'ministry': 'Government of India',
                            'beneficiary': 'Eligible Citizens',
                            'deadline': 'Ongoing',
                            'url': link['href'] if link['href'].startswith('http') else source['url'] + link['href'],
                            'category': self.determine_category(text),
                            'source': source['name'],
                            'scraped_date': datetime.now().strftime('%Y-%m-%d')
                        }
                        
                        all_schemes.append(scheme)
                
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error scraping {source['name']}: {str(e)}")
                continue
        
        return all_schemes
    
    def determine_category(self, title):
        """Determine scheme category"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['farmer', 'kisan', 'agriculture']):
            return 'agriculture'
        elif any(word in title_lower for word in ['student', 'education', 'school']):
            return 'education'
        elif any(word in title_lower for word in ['health', 'medical', 'hospital']):
            return 'health'
        elif any(word in title_lower for word in ['women', 'mahila', 'female']):
            return 'women'
        elif any(word in title_lower for word in ['rural', 'village', 'gramin']):
            return 'rural'
        else:
            return 'general'