import os
import sys
import time
import logging
import threading
import schedule
from datetime import datetime
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/job_scraper.log')
    ]
)

# Import scrapers
from scrapers.government_scraper import GovernmentJobScraper
from scrapers.private_scraper import PrivateJobScraper
from scrapers.schemes_scraper import GovernmentSchemesScraper
from scrapers.notifications_scraper import NotificationsScraper
from scrapers.welfare_scraper import WelfareProgramsScraper

# Import utilities
from utils.whatsapp_sender import WhatsAppStatusSender
from utils.job_validator import ContentValidator
from utils.image_generator import ContentImageGenerator
from utils.database import Database

# Create Flask app for health checks
app = Flask(__name__)

class ContentScraperTool:
    def __init__(self):
        """Initialize all components"""
        logging.info("Initializing Content Scraper Tool...")
        
        # Initialize database
        self.db = Database()
        
        # Initialize validators
        self.validator = ContentValidator()
        
        # Initialize scrapers
        self.gov_scraper = GovernmentJobScraper()
        self.private_scraper = PrivateJobScraper()
        self.schemes_scraper = GovernmentSchemesScraper()
        self.notifications_scraper = NotificationsScraper()
        self.welfare_scraper = WelfareProgramsScraper()
        
        # Initialize WhatsApp sender
        self.whatsapp_sender = WhatsAppStatusSender()
        
        # Initialize image generator
        self.image_generator = ContentImageGenerator()
        
        logging.info("Initialization complete!")
    
    def scrape_all_content(self):
        """Scrape all types of content"""
        all_items = []
        
        try:
            # Scrape government jobs
            logging.info("Scraping government jobs...")
            gov_jobs = self.gov_scraper.scrape()
            for job in gov_jobs:
                job['content_type'] = 'job'
                job['sub_type'] = 'government'
            all_items.extend(gov_jobs)
            logging.info(f"Found {len(gov_jobs)} government jobs")
            
            # Scrape private jobs
            logging.info("Scraping private jobs...")
            private_jobs = self.private_scraper.scrape()
            for job in private_jobs:
                job['content_type'] = 'job'
                job['sub_type'] = 'private'
            all_items.extend(private_jobs)
            logging.info(f"Found {len(private_jobs)} private jobs")
            
            # Scrape government schemes
            logging.info("Scraping government schemes...")
            schemes = self.schemes_scraper.scrape_all_schemes()
            for scheme in schemes:
                scheme['content_type'] = 'scheme'
            all_items.extend(schemes)
            logging.info(f"Found {len(schemes)} government schemes")
            
            # Scrape notifications
            logging.info("Scraping notifications...")
            notifications = self.notifications_scraper.scrape_all_notifications()
            for note in notifications:
                note['content_type'] = 'notification'
            all_items.extend(notifications)
            logging.info(f"Found {len(notifications)} notifications")
            
            # Scrape welfare programs
            logging.info("Scraping welfare programs...")
            welfare = self.welfare_scraper.scrape_welfare_programs()
            for prog in welfare:
                prog['content_type'] = 'welfare'
            all_items.extend(welfare)
            logging.info(f"Found {len(welfare)} welfare programs")
            
            # Sort by priority (urgent notifications first)
            all_items.sort(key=lambda x: self.get_priority_score(x), reverse=True)
            
        except Exception as e:
            logging.error(f"Error in scraping: {str(e)}")
        
        return all_items
    
    def get_priority_score(self, item):
        """Calculate priority score for sorting"""
        score = 0
        
        if item.get('content_type') == 'notification':
            days = item.get('days_remaining', 30)
            if days and days < 7:
                score += 100  # Urgent notifications
            elif days and days < 15:
                score += 50
                
        if item.get('content_type') == 'job':
            score += 30
            
        if item.get('content_type') == 'scheme':
            if item.get('deadline') != 'Ongoing':
                score += 20
            else:
                score += 10
                
        if item.get('importance') == 'high':
            score += 25
            
        return score
    
    def validate_and_save(self, items):
        """Validate items and save to database"""
        valid_items = []
        
        for item in items:
            if self.validator.validate_item(item):
                # Check if already exists
                if not self.db.item_exists(item):
                    self.db.save_item(item)
                    valid_items.append(item)
        
        return valid_items
    
    def post_to_whatsapp(self, items):
        """Post items to WhatsApp status"""
        if not items:
            logging.info("No new items to post")
            return
        
        # Limit to 5 posts per day to avoid spam
        items = items[:5]
        
        for item in items:
            try:
                # Generate appropriate text
                status_text = self.create_status_text(item)
                
                # Generate image
                image_path = self.image_generator.create_image(item)
                
                # Post to WhatsApp
                self.whatsapp_sender.post_status(
                    text=status_text,
                    image_path=image_path
                )
                
                logging.info(f"Posted: {item.get('title', 'Unknown')}")
                
                # Mark as posted in database
                self.db.mark_as_posted(item)
                
                # Wait between posts
                time.sleep(10)
                
            except Exception as e:
                logging.error(f"Error posting item: {str(e)}")
                continue
    
    def create_status_text(self, item):
        """Create formatted text based on content type"""
        content_type = item.get('content_type', 'general')
        
        if content_type == 'job':
            return self.format_job_status(item)
        elif content_type == 'scheme':
            return self.format_scheme_status(item)
        elif content_type == 'notification':
            return self.format_notification_status(item)
        elif content_type == 'welfare':
            return self.format_welfare_status(item)
        else:
            return self.format_general_status(item)
    
    def format_job_status(self, job):
        """Format job posting"""
        emoji = '🏛️' if job.get('sub_type') == 'government' else '💼'
        
        text = f"{emoji} *JOB VACANCY* {emoji}\n\n"
        text += f"*{job.get('title', 'N/A')}*\n"
        text += f"🏢 {job.get('company', 'N/A')}\n"
        text += f"📍 {job.get('location', 'India')}\n"
        
        if job.get('salary'):
            text += f"💰 {job['salary']}\n"
            
        if job.get('last_date'):
            text += f"📅 Last Date: {job['last_date']}\n"
        
        text += f"\n🔗 Apply: {job.get('url', 'Link in bio')}\n\n"
        
        if job.get('sub_type') == 'government':
            text += f"#SarkariNaukri #GovtJobs #{job.get('category', 'job')}"
        else:
            text += f"#PrivateJobs #Hiring #{job.get('category', 'job')}"
        
        return text
    
    def format_scheme_status(self, scheme):
        """Format government scheme"""
        category_emoji = {
            'agriculture': '🌾', 'education': '📚', 'health': '🏥',
            'women': '👩', 'rural': '🏡', 'business': '💼',
            'housing': '🏠', 'employment': '👷', 'social': '🤝'
        }
        
        emoji = category_emoji.get(scheme.get('category', 'general'), '🇮🇳')
        
        text = f"{emoji} *GOVERNMENT SCHEME* {emoji}\n\n"
        text += f"*{scheme.get('title', 'N/A')}*\n"
        text += f"🏛️ {scheme.get('ministry', 'Govt of India')}\n"
        text += f"👥 For: {scheme.get('beneficiary', 'All Citizens')}\n\n"
        text += f"📝 {scheme.get('description', '')}\n\n"
        
        if scheme.get('deadline') and scheme['deadline'] != 'Ongoing':
            text += f"⏰ Apply by: {scheme['deadline']}\n"
        
        text += f"🔗 Details: {scheme.get('url', 'Link in bio')}\n\n"
        text += f"#{scheme.get('category', 'scheme')}Scheme #SarkariYojana"
        
        return text
    
    def format_notification_status(self, notification):
        """Format notification"""
        importance = notification.get('importance', 'medium')
        
        if importance == 'high':
            emoji = '🔴'
            urgency = "URGENT!"
        elif importance == 'medium':
            emoji = '🟡'
            urgency = "Reminder"
        else:
            emoji = '🟢'
            urgency = "Upcoming"
        
        text = f"{emoji} *{urgency}* {emoji}\n\n"
        text += f"*{notification.get('title', 'N/A')}*\n\n"
        
        if notification.get('exam_date'):
            text += f"📅 Exam Date: {notification['exam_date']}\n"
            
        if notification.get('last_date'):
            text += f"📆 Last Date: {notification['last_date']}\n"
            
        days = notification.get('days_remaining')
        if days and days > 0:
            text += f"⏳ {days} days remaining!\n"
        elif days and days < 0:
            text += f"❌ EXPIRED ({(days*-1)} days ago)\n"
        
        text += f"\n🔗 More info: {notification.get('url', 'Link in bio')}\n\n"
        text += f"#{notification.get('source')} #Notification #ExamUpdate"
        
        return text
    
    def format_welfare_status(self, program):
        """Format welfare program"""
        text = f"🤝 *WELFARE PROGRAM* 🤝\n\n"
        text += f"*{program.get('title', 'N/A')}*\n"
        text += f"👥 For: {program.get('target_beneficiaries', 'All')}\n\n"
        text += f"📝 {program.get('description', '')}\n\n"
        text += f"🔗 Check eligibility: {program.get('url', 'Link in bio')}\n\n"
        text += f"#Welfare #{program.get('category', 'social')} #SocialJustice"
        
        return text
    
    def format_general_status(self, item):
        """Format general item"""
        text = f"📢 *NEW UPDATE* 📢\n\n"
        text += f"*{item.get('title', 'N/A')}*\n\n"
        text += f"{item.get('description', '')}\n\n"
        text += f"🔗 {item.get('url', 'Link in bio')}"
        
        return text
    
    def run_once(self):
        """Run the scraper once"""
        logging.info("Starting single scraping run...")
        
        # Scrape all content
        all_items = self.scrape_all_content()
        
        # Validate and save
        new_items = self.validate_and_save(all_items)
        
        # Post to WhatsApp
        self.post_to_whatsapp(new_items)
        
        logging.info(f"Completed! Found {len(all_items)} total items, {len(new_items)} new items posted.")
    
    def run_scheduled(self):
        """Run on schedule"""
        # Get schedule times from environment
        morning_time = os.getenv('MORNING_POST_TIME', '09:00')
        evening_time = os.getenv('EVENING_POST_TIME', '18:00')
        
        logging.info(f"Scheduling posts at {morning_time} and {evening_time}")
        
        # Schedule jobs
        schedule.every().day.at(morning_time).do(self.run_once)
        schedule.every().day.at(evening_time).do(self.run_once)
        
        # Run once at startup
        self.run_once()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)

# Flask routes for health checks
@app.route('/')
def home():
    return jsonify({
        'status': 'healthy',
        'service': 'Job Scraper Tool',
        'version': '2.0',
        'time': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}),200

@app.route('/stats')
def stats():
    db = Database()
    return jsonify(db.get_stats())

def run_flask():
    """Run Flask server"""
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    logging.info("Starting Job Scraper Tool on Railway")
    
    # Start Flask server in a thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run the scraper
    scraper = ContentScraperTool()
    
    try:
        scraper.run_scheduled()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)
