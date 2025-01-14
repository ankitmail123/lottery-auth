import os
import json
import time
import hmac
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import qrcode
from PIL import Image
import io
import hashlib
import base64
import numpy as np
import cv2
from qrcode.image.pil import PilImage
from qrcode.constants import ERROR_CORRECT_H
import secrets

class LogoQR(PilImage):
    """Custom QR code image class that creates a blank space in the center"""
    def __init__(self, border, width, box_size, *args, **kwargs):
        super().__init__(border, width, box_size, *args, **kwargs)
        # Calculate center size based on version (1/3 of data area)
        self.center_size = (width - 8) // 3  # Exclude quiet zone (4 modules on each side)
        self.center_offset = (width - self.center_size) // 2
        
        # Create a white rectangle in the center
        self._idr.rectangle([
            self.center_offset * self.box_size + self.border,
            self.center_offset * self.box_size + self.border,
            (self.center_offset + self.center_size) * self.box_size + self.border,
            (self.center_offset + self.center_size) * self.box_size + self.border
        ], fill="white")
        
    def drawrect(self, row, col):
        """Draw a single box, but skip if in the center area"""
        # Check if we're in the center area
        if (self.center_offset <= row < self.center_offset + self.center_size and 
            self.center_offset <= col < self.center_offset + self.center_size):
            # Skip drawing in center area
            return
        
        # Draw normal QR code box
        super().drawrect(row, col)

class TicketGenerator:
    def __init__(self, secret_key=None):
        """Initialize the ticket generator with a secret key"""
        self.secret_key = secret_key if secret_key else hashlib.sha256().digest()
    
    def generate_ticket_data(self, ticket_id, draw_date=None, ticket_price=None, draw_number=None):
        """Generate ticket data with HMAC"""
        # Current timestamp
        current_time = int(time.mktime(time.strptime("2025-01-14T09:30:39+05:30", "%Y-%m-%dT%H:%M:%S%z")))
        
        # Default draw date (7 days from now)
        if draw_date is None:
            draw_date = current_time + (7 * 24 * 60 * 60)
        
        # Create ticket data
        ticket_data = {
            'id': ticket_id,  # Ticket ID
            't': current_time,  # Generation timestamp
            'd': draw_date,  # Draw date
        }
        
        # Add optional fields
        if ticket_price is not None:
            ticket_data['p'] = ticket_price
        if draw_number is not None:
            ticket_data['n'] = draw_number
        
        # Generate HMAC
        hmac_data = json.dumps(ticket_data, sort_keys=True).encode()
        ticket_data['h'] = self.generate_hmac(hmac_data)
        
        return ticket_data

    def generate_hmac(self, data):
        return base64.b64encode(
            hashlib.sha256(
                f"{data}:{self.secret_key.hex()}".encode()
            ).digest()
        ).decode()

    def generate_inner_qr_data(self, ticket_data):
        """Generate inner QR data"""
        # Create inner QR data with last 4 digits and timestamp
        inner_data = {
            'l4': ticket_data['id'][-4:],  # Last 4 digits of ticket ID
            'ts': int(time.time())  # Add timestamp for additional security
        }
        
        return inner_data, None  # No distortion key needed

    def apply_distortion(self, image, distortion_key):
        """No distortion applied, return image as is"""
        return image

    def generate_composite_qr(self, ticket_id, output_path, draw_date=None, ticket_price=None, draw_number=None):
        """Generate composite QR code with inner verification"""
        # Generate main ticket data
        ticket_data = self.generate_ticket_data(ticket_id, draw_date, ticket_price, draw_number)
        
        # Generate inner QR data
        inner_data, _ = self.generate_inner_qr_data(ticket_data)
        
        # Create main QR code with higher error correction and center space
        qr = qrcode.QRCode(
            version=4,  # Smaller version for better readability
            error_correction=ERROR_CORRECT_H,
            box_size=15,  # Larger box size for better scanning
            border=4,
            image_factory=LogoQR
        )
        qr.add_data(json.dumps(ticket_data))
        qr.make(fit=True)
        
        # Generate main QR with white background
        main_qr = qr.make_image(fill_color="black", back_color="white")
        
        # Get center size and position from QR code
        width = qr.modules_count
        center_size = (width - 8) // 3  # Same calculation as in LogoQR
        center_offset = (width - center_size) // 2
        
        # Convert sizes to pixels
        center_size_px = center_size * qr.box_size
        center_pos_px = center_offset * qr.box_size + qr.border * qr.box_size
        
        # Create inner QR with smaller version and higher error correction
        inner_qr = qrcode.QRCode(
            version=1,  # Smallest version for inner QR
            error_correction=ERROR_CORRECT_H,
            box_size=8,  # Increased for better readability
            border=2  # Increased border for better recognition
        )
        inner_qr.add_data(json.dumps(inner_data))
        inner_qr.make(fit=True)
        
        # Create and resize inner QR
        inner_img = inner_qr.make_image(fill_color="black", back_color="white")
        
        # Calculate optimal size with padding
        padding = 40  # Increased padding
        target_size = center_size_px - padding
        inner_img = inner_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # No distortion applied
        
        # Convert both images to RGB
        main_qr = main_qr.convert("RGB")
        inner_img = inner_img.convert("RGB")
        
        # Create a white background for inner QR
        bg = Image.new('RGB', (center_size_px, center_size_px), 'white')
        
        # Center the inner QR in the background
        paste_x = (center_size_px - inner_img.size[0]) // 2
        paste_y = (center_size_px - inner_img.size[1]) // 2
        bg.paste(inner_img, (paste_x, paste_y))
        
        # Paste inner QR into center space
        main_qr_copy = main_qr.copy()
        main_qr_copy.paste(bg, (center_pos_px, center_pos_px))
        
        # Save composite QR with high quality
        main_qr_copy.save(output_path, quality=100)
        
        return ticket_data

if __name__ == "__main__":
    # Demo usage
    generator = TicketGenerator()
    ticket_id = "TKT12345"
    encoded = generator.generate_composite_qr(ticket_id, "sample_ticket.png")
    print(f"Generated QR code with data: {encoded}")
