import os
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any

class Database:
    def __init__(self):
        """Initialize database connection"""
        self.db_path = '/tmp/scraper.db'
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT,
                    location TEXT,
                    salary TEXT,
                    last_date TEXT,
                    url TEXT,
                    source TEXT,
                    sub_type TEXT,
                    scraped_date TEXT,
                    posted_date TEXT,
                    is_posted INTEGER DEFAULT 0,
                    UNIQUE(title, company, source)
                )
            ''')
            
            # Create schemes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schemes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    ministry TEXT,
                    beneficiary TEXT,
                    deadline TEXT,
                    url TEXT,
                    category TEXT,
                    source TEXT,
                    scraped_date TEXT,
                    posted_date TEXT,
                    is_posted INTEGER DEFAULT 0,
                    UNIQUE(title, source)
                )
            ''')
            
            # Create notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    type TEXT,
                    notification_date TEXT,
                    last_date TEXT,
                    exam_date TEXT,
                    days_remaining INTEGER,
                    importance TEXT,
                    url TEXT,
                    source TEXT,
                    scraped_date TEXT,
                    posted_date TEXT,
                    is_posted INTEGER DEFAULT 0,
                    UNIQUE(title, source)
                )
            ''')
            
            # Create welfare table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS welfare (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    target_beneficiaries TEXT,
                    category TEXT,
                    url TEXT,
                    source TEXT,
                    scraped_date TEXT,
                    posted_date TEXT,
                    is_posted INTEGER DEFAULT 0,
                    UNIQUE(title, source)
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info("Database initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
    
    def item_exists(self, item: Dict[str, Any]) -> bool:
        """Check if item already exists in database"""
        content_type = item.get('content_type', 'job')
        table_map = {
            'job': 'jobs',
            'scheme': 'schemes',
            'notification': 'notifications',
            'welfare': 'welfare'
        }
        
        table = table_map.get(content_type, 'jobs')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                SELECT id FROM {table} 
                WHERE title = ? AND source = ?
            ''', (item.get('title', ''), item.get('source', '')))
            
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
            
        except Exception as e:
            logging.error(f"Error checking item existence: {str(e)}")
            return False
    
    def save_item(self, item: Dict[str, Any]):
        """Save item to appropriate table"""
        content_type = item.get('content_type', 'job')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if content_type == 'job':
                cursor.execute('''
                    INSERT OR IGNORE INTO jobs 
                    (title, company, location, salary, last_date, url, source, sub_type, scraped_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('title', ''),
                    item.get('company', ''),
                    item.get('location', ''),
                    item.get('salary', ''),
                    item.get('last_date', ''),
                    item.get('url', ''),
                    item.get('source', ''),
                    item.get('sub_type', 'private'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
            elif content_type == 'scheme':
                cursor.execute('''
                    INSERT OR IGNORE INTO schemes 
                    (title, description, ministry, beneficiary, deadline, url, category, source, scraped_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('title', ''),
                    item.get('description', ''),
                    item.get('ministry', ''),
                    item.get('beneficiary', ''),
                    item.get('deadline', ''),
                    item.get('url', ''),
                    item.get('category', ''),
                    item.get('source', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
            elif content_type == 'notification':
                cursor.execute('''
                    INSERT OR IGNORE INTO notifications 
                    (title, type, notification_date, last_date, exam_date, days_remaining, importance, url, source, scraped_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('title', ''),
                    item.get('type', ''),
                    item.get('notification_date', ''),
                    item.get('last_date', ''),
                    item.get('exam_date', ''),
                    item.get('days_remaining', 0),
                    item.get('importance', 'medium'),
                    item.get('url', ''),
                    item.get('source', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
            elif content_type == 'welfare':
                cursor.execute('''
                    INSERT OR IGNORE INTO welfare 
                    (title, description, target_beneficiaries, category, url, source, scraped_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('title', ''),
                    item.get('description', ''),
                    item.get('target_beneficiaries', ''),
                    item.get('category', ''),
                    item.get('url', ''),
                    item.get('source', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error saving item: {str(e)}")
    
    def mark_as_posted(self, item: Dict[str, Any]):
        """Mark item as posted"""
        content_type = item.get('content_type', 'job')
        table_map = {
            'job': 'jobs',
            'scheme': 'schemes',
            'notification': 'notifications',
            'welfare': 'welfare'
        }
        
        table = table_map.get(content_type, 'jobs')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                UPDATE {table} 
                SET is_posted = 1, posted_date = ?
                WHERE title = ? AND source = ?
            ''', (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                item.get('title', ''),
                item.get('source', '')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error marking item as posted: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            'total_jobs': 0,
            'total_schemes': 0,
            'total_notifications': 0,
            'total_welfare': 0,
            'posted_today': 0
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM jobs")
            stats['total_jobs'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM schemes")
            stats['total_schemes'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM notifications")
            stats['total_notifications'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM welfare")
            stats['total_welfare'] = cursor.fetchone()[0]
            
            # Get posted today
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE posted_date LIKE ? || '%'", (today,))
            stats['posted_today'] += cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM schemes WHERE posted_date LIKE ? || '%'", (today,))
            stats['posted_today'] += cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM notifications WHERE posted_date LIKE ? || '%'", (today,))
            stats['posted_today'] += cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM welfare WHERE posted_date LIKE ? || '%'", (today,))
            stats['posted_today'] += cursor.fetchone()[0]
            
            conn.close()
            
        except Exception as e:
            logging.error(f"Error getting stats: {str(e)}")
        
        return stats