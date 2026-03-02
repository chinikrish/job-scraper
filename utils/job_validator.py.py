import re
import logging

class ContentValidator:
    def __init__(self):
        self.blocked_keywords = [
            'fraud', 'scam', 'fake', 'spam', 'earn money fast',
            'work from home without investment', 'data entry without investment',
            'pyramid', 'chain', 'mlm', 'get rich quick'
        ]
        
        self.required_fields = {
            'job': ['title', 'company'],
            'scheme': ['title', 'ministry'],
            'notification': ['title'],
            'welfare': ['title']
        }
    
    def validate_item(self, item):
        """Validate if item is genuine"""
        try:
            content_type = item.get('content_type', 'job')
            
            # Check required fields
            required = self.required_fields.get(content_type, ['title'])
            for field in required:
                if field not in item or not item.get(field):
                    return False
            
            # Check for blocked keywords in title
            title = item.get('title', '').lower()
            for keyword in self.blocked_keywords:
                if keyword in title:
                    return False
            
            # Check minimum title length
            if len(item.get('title', '')) < 5:
                return False
            
            return True
            
        except Exception:
            return False