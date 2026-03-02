from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

class ContentImageGenerator:
    def __init__(self):
        self.output_dir = '/tmp/status_images'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Use default font
        try:
            self.title_font = ImageFont.truetype("arial.ttf", 40)
            self.body_font = ImageFont.truetype("arial.ttf", 30)
        except:
            self.title_font = ImageFont.load_default()
            self.body_font = ImageFont.load_default()
    
    def create_image(self, item):
        """Create a simple image for the post"""
        # Create image
        img = Image.new('RGB', (1080, 1080), color='#1e3c72')
        draw = ImageDraw.Draw(img)
        
        # Draw title
        y_position = 200
        title = item.get('title', 'New Update')[:50]
        
        try:
            draw.text((540, y_position), title, fill='white', font=self.title_font, anchor='mm')
        except:
            draw.text((540, y_position), title, fill='white', anchor='mm')
        
        # Draw type
        y_position += 100
        content_type = item.get('content_type', 'Update').upper()
        
        try:
            draw.text((540, y_position), content_type, fill='#ffd700', font=self.body_font, anchor='mm')
        except:
            draw.text((540, y_position), content_type, fill='#ffd700', anchor='mm')
        
        # Save image
        filename = f"status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)
        
        return filepath