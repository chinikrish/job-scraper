import requests
from bs4 import BeautifulSoup
import logging
import re
from datetime import datetime
from fake_useragent import UserAgent

class NotificationsScraper:
    def __init__(self):
        self.notification_sources = [
            {
                'name': 'UPSC',
                'url': 'https://upsc.gov.in/examinations/calendar',
                'type': 'exam_calendar'
            },
            {
                'name': 'SSC',
                'url': 'https://ssc.nic.in/SSC_Notifications',
                'type': 'recruitment'
            }
        ]
    
    def scrape_all_notifications(self):
        """Scrape all upcoming notifications"""
        all_notifications = []
        
        for source in self.notification_sources:
            try:
                logging.info(f"Scraping notifications from {source['name']}...")
                
                headers = {'User-Agent': UserAgent().random}
                response = requests.get(source['url'], headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find notification links
                for link in soup.find_all('a', href=True)[:15]:
                    text = link.text
                    
                    if len(text) > 10 and ('notification' in text.lower() or 'exam' in text.lower()):
                        # Try to extract dates
                        dates = self.extract_dates(text)
                        
                        notification = {
                            'title': text.strip(),
                            'type': 'exam_notification',
                            'last_date': dates.get('last_date', 'Check website'),
                            'days_remaining': dates.get('days', 30),
                            'importance': 'medium',
                            'url': link['href'] if link['href'].startswith('http') else source['url'] + link['href'],
                            'source': source['name'],
                            'scraped_date': datetime.now().strftime('%Y-%m-%d')
                        }
                        
                        all_notifications.append(notification)
                
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error scraping {source['name']}: {str(e)}")
                continue
        
        return all_notifications
    
    def extract_dates(self, text):
        """Extract dates from text"""
        result = {'last_date': 'Check website', 'days': 30}
        
        # Look for date patterns
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        dates = re.findall(date_pattern, text)
        
        if dates:
            result['last_date'] = dates[-1]  # Use last date found
            
        return result