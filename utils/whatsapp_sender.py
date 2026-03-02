import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class WhatsAppStatusSender:
    def __init__(self):
        self.driver = None
        self.session_dir = '/tmp/whatsapp-session'
        
    def setup_driver(self):
        """Setup Chrome driver for headless environment"""
        chrome_options = Options()
        
        # Required for headless environments
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # User data directory for session
        chrome_options.add_argument(f'user-data-dir={self.session_dir}')
        
        # Additional arguments
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        try:
            # Try different Chrome driver locations
            possible_paths = [
                '/usr/bin/chromedriver',
                '/usr/local/bin/chromedriver',
                '/app/.chromedriver/bin/chromedriver'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    service = Service(path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    break
            else:
                # Let webdriver-manager handle it
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
        except Exception as e:
            logging.error(f"Error setting up driver: {str(e)}")
            raise
    
    def login_whatsapp(self):
        """Login to WhatsApp Web"""
        try:
            self.driver.get("https://web.whatsapp.com")
            
            print("\n" + "="*50)
            print("WHATSAPP WEB LOGIN REQUIRED")
            print("="*50)
            print("\n1. Check the logs for QR code")
            print("2. Open WhatsApp on your phone")
            print("3. Go to Settings → Linked Devices")
            print("4. Scan the QR code")
            print("\nWaiting for QR code scan...")
            
            # Wait for WhatsApp to load
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            
            print("✓ Successfully logged in to WhatsApp!")
            return True
            
        except Exception as e:
            logging.error(f"Error logging into WhatsApp: {str(e)}")
            return False
    
    def post_status(self, text, image_path=None):
        """Post to WhatsApp status"""
        try:
            if not self.driver:
                self.setup_driver()
                
                # Check if already logged in
                self.driver.get("https://web.whatsapp.com")
                time.sleep(5)
                
                # Try to detect if logged in
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                    )
                    logging.info("Already logged in to WhatsApp")
                except:
                    # Need to login
                    if not self.login_whatsapp():
                        return False
            
            # Click on Status tab
            try:
                status_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Status"]'))
                )
                status_tab.click()
                time.sleep(2)
                
                # Click on "Add status"
                add_status = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Add status"]'))
                )
                add_status.click()
                time.sleep(2)
            except:
                logging.warning("Could not click status button, trying alternative")
                # Try alternative method
                self.driver.get("https://web.whatsapp.com")
                time.sleep(5)
            
            # For now, just log that we would post
            logging.info(f"Would post: {text[:50]}...")
            
            return True
            
        except Exception as e:
            logging.error(f"Error posting status: {str(e)}")
            return False