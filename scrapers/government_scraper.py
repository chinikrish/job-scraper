import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from fake_useragent import UserAgent

class GovernmentJobScraper:
    def __init__(self):
        self.sources = [
            {
                'name': 'Employment News',
                'url': 'https://employmentnews.gov.in/',
                'type': 'general'
            },
            {
                'name': 'Sarkari Result',
                'url': 'https://www.sarkariresult.com/',
                'type': 'aggregator'
            },
            {
                'name': 'FreeJobAlert',
                'url': 'https://www.freejobalert.com/',
                'type': 'aggregator'
            }
        ]
    
    def scrape(self):
        """Main scraping function"""
        all_jobs = []
        
        for source in self.sources:
            try:
                logging.info(f"Scraping {source['name']}...")
                
                headers = {'User-Agent': UserAgent().random}
                response = requests.get(source['url'], headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job listings
                for link in soup.find_all('a', href=True)[:10]:
                    text = link.text.lower()
                    
                    job_keywords = ['recruitment', 'job', 'vacancy', 'apply', 'notification']
                    
                    if any(keyword in text for keyword in job_keywords):
                        job = {
                            'title': link.text.strip()[:100],
                            'company': source['name'],
                            'location': 'India',
                            'last_date': 'Check website',
                            'url': link['href'] if link['href'].startswith('http') else source['url'] + link['href'],
                            'source': source['name'],
                            'scraped_date': time.strftime('%Y-%m-%d')
                        }
                        
                        all_jobs.append(job)
                
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logging.error(f"Error scraping {source['name']}: {str(e)}")
                continue
        
        return all_jobs