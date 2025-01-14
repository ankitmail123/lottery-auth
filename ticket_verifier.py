import os
import time
import hashlib
import base64
import json
from datetime import datetime
import numpy as np
from PIL import Image
import cv2
from pyzbar.pyzbar import decode
import secrets
import qrcode
import qrcode.image
from Crypto.Cipher import AES

class TicketVerifier:
    def __init__(self, secret_key):
        """Initialize the ticket verifier with a secret key"""
        self.secret_key = secret_key if secret_key else hashlib.sha256().digest()
        self.used_tickets = set()

    def scan_qr_image(self, image, is_inner=False):
        """Scan QR image and return decoded data using multiple methods"""
        try:
            print(f"Scanning {'inner' if is_inner else 'main'} QR image...")
            # Convert PIL Image to numpy array
            np_image = np.array(image).astype(np.uint8)
            
            # Convert to grayscale if needed
            if len(np_image.shape) == 3:
                np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
            
            # Enhance contrast
            enhanced = cv2.equalizeHist(np_image)
            
            # Try different methods to decode
            
            # 1. Try direct scan
            decoded_objects = decode(enhanced)
            if decoded_objects:
                # Sort by size (main QR will be larger than inner QR)
                decoded_objects.sort(key=lambda x: x.rect.width * x.rect.height, reverse=True)
                
                # For inner QR, take any QR code
                # For main QR, take the largest one
                qr_code = decoded_objects[-1] if is_inner else decoded_objects[0]
                
                print(f"Decoded QR code using direct scan")
                data = qr_code.data.decode('utf-8')
                print(f"Decoded data: {data}")
                try:
                    return json.loads(data)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    return None
            
            # 2. Try Otsu's thresholding
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            decoded_objects = decode(binary)
            if decoded_objects:
                # Sort by size
                decoded_objects.sort(key=lambda x: x.rect.width * x.rect.height, reverse=True)
                qr_code = decoded_objects[-1] if is_inner else decoded_objects[0]
                
                print(f"Decoded QR code using Otsu's thresholding")
                data = qr_code.data.decode('utf-8')
                print(f"Decoded data: {data}")
                try:
                    return json.loads(data)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    return None
            
            # 3. Try multiple scales
            for scale in [0.5, 1.5, 2.0]:
                height, width = np_image.shape
                new_height = int(height * scale)
                new_width = int(width * scale)
                resized = cv2.resize(enhanced, (new_width, new_height))
                decoded_objects = decode(resized)
                if decoded_objects:
                    # Sort by size
                    decoded_objects.sort(key=lambda x: x.rect.width * x.rect.height, reverse=True)
                    qr_code = decoded_objects[-1] if is_inner else decoded_objects[0]
                    
                    print(f"Decoded QR code using scale {scale}")
                    data = qr_code.data.decode('utf-8')
                    print(f"Decoded data: {data}")
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        return None
            
            print("Failed to decode QR code")
            return None
        except Exception as e:
            print(f"Error scanning QR: {str(e)}")
            return None

    def extract_inner_qr(self, image):
        """Extract the inner QR code from the composite image"""
        try:
            print("Extracting inner QR code...")
            # Convert PIL Image to numpy array
            np_image = np.array(image).astype(np.uint8)
            
            # Convert to grayscale if needed
            if len(np_image.shape) == 3:
                np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
            
            # Get image dimensions
            height, width = np_image.shape
            
            # Calculate center position and size (1/3 of total size)
            center_size = min(width, height) // 3
            start_x = (width - center_size) // 2
            start_y = (height - center_size) // 2
            
            # Extract inner QR with padding
            padding = 10
            inner_qr = np_image[
                start_y + padding:start_y + center_size - padding,
                start_x + padding:start_x + center_size - padding
            ]
            
            # Apply multiple preprocessing steps
            # 1. Enhance contrast
            enhanced = cv2.equalizeHist(inner_qr)
            
            # 2. Denoise
            denoised = cv2.fastNlMeansDenoising(enhanced)
            
            # 3. Sharpen
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            # 4. Adaptive threshold
            binary = cv2.adaptiveThreshold(
                sharpened,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                15,
                5
            )
            
            print("Inner QR code extracted")
            return Image.fromarray(binary)
        except Exception as e:
            print(f"Error extracting inner QR: {str(e)}")
            return None

    def recover_inner_qr(self, inner_qr_image, ticket_data):
        """No recovery needed, return image as is"""
        return inner_qr_image

    def decode_inner_data(self, inner_data, ticket_data):
        """Decode and verify the inner QR data"""
        try:
            # Generate distortion key
            distortion_key = hashlib.sha256(
                f"{ticket_data['id']}:{ticket_data['ts']}:{self.secret_key.hex()}".encode()
            ).digest()
            
            # Decode components
            nonce = base64.b64decode(inner_data['n'])
            encrypted_digits = base64.b64decode(inner_data['e'])
            tag = base64.b64decode(inner_data['t'])
            
            # Decrypt last 4 digits
            cipher = AES.new(distortion_key[:32], AES.MODE_GCM, nonce=nonce)
            decrypted_digits = cipher.decrypt_and_verify(encrypted_digits, tag)
            
            return decrypted_digits.decode('utf-8')
        except Exception as e:
            return None
    
    def verify_ticket_data(self, ticket_data):
        """Verify the ticket data and HMAC"""
        try:
            # Extract HMAC
            hmac = ticket_data.pop('h', None)
            if not hmac:
                return False, "Missing HMAC"
            
            # Verify HMAC
            expected_hmac = self.generate_hmac(json.dumps(ticket_data, sort_keys=True))
            if hmac != expected_hmac:
                return False, "Invalid HMAC"
            
            # Verify timestamp (allow verification within 24 hours)
            timestamp = ticket_data.get('t')
            if not timestamp:
                return False, "Missing timestamp"
            
            current_time = int(time.mktime(time.strptime("2025-01-14T08:27:36+05:30", "%Y-%m-%dT%H:%M:%S%z")))
            if abs(current_time - timestamp) > 24*60*60:
                return False, "Ticket expired or not yet valid"
            
            return True, "Valid ticket"
        except Exception as e:
            return False, f"Error verifying ticket: {str(e)}"

    def verify_inner_qr(self, inner_data, ticket_id):
        """Verify the inner QR data"""
        try:
            # Verify last 4 digits
            last_four = inner_data.get('l4', '')
            if not last_four or len(last_four) != 4:
                return None, "Invalid inner QR data"
            
            # Check if last 4 digits match
            if not ticket_id.endswith(last_four):
                return None, "Inner QR verification failed"
            
            # Verify timestamp is present
            if 'ts' not in inner_data:
                return None, "Missing timestamp in inner QR"
            
            return last_four, None
        except Exception as e:
            return None, f"Error verifying inner QR: {str(e)}"

    def generate_hmac(self, data):
        """Generate HMAC for verification"""
        return base64.b64encode(
            hashlib.sha256(
                f"{data}:{self.secret_key.hex()}".encode()
            ).digest()
        ).decode()
    
    def verify_composite_qr(self, qr_path):
        """Verify a composite QR code"""
        try:
            # Read QR code image
            image = Image.open(qr_path)
            
            # Scan main QR code
            main_data = self.scan_qr_image(image, is_inner=False)
            if not main_data:
                return False, "Could not read main QR code"
            
            # Extract inner QR
            inner_qr = self.extract_inner_qr(image)
            if inner_qr is None:
                return False, "Could not extract inner QR code"
            
            # Try to read the QR code directly
            inner_data = self.scan_qr_image(inner_qr, is_inner=True)
            if not inner_data:
                return False, "Could not read inner QR code"
            
            # Verify inner data
            last_four, error = self.verify_inner_qr(inner_data, main_data['id'])
            if error:
                return False, error
            
            # Current timestamp
            current_time = int(time.mktime(time.strptime("2025-01-14T09:30:39+05:30", "%Y-%m-%dT%H:%M:%S%z")))
            
            # Validation checks
            if main_data.get('t', 0) > current_time:
                return False, "Invalid ticket date"
            
            if main_data.get('d', 0) < current_time:
                return False, "Ticket expired (draw date passed)"
            
            if main_data['id'] in self.used_tickets:
                return False, "Ticket already used"
            
            # Mark ticket as used
            self.used_tickets.add(main_data['id'])
            
            return True, {
                "status": "Valid",
                "ticket_id": main_data['id'],
                "draw_date": datetime.fromtimestamp(main_data['d']).strftime('%Y-%m-%d %H:%M:%S'),
                "draw_number": main_data.get('n', 0),
                "ticket_price": main_data.get('p', 0)
            }
            
        except Exception as e:
            return False, f"Error verifying QR code: {str(e)}"

if __name__ == "__main__":
    # Demo usage
    from ticket_generator import TicketGenerator
    
    # Create generator and verifier with same key
    generator = TicketGenerator()
    verifier = TicketVerifier(generator.secret_key)
    
    # Generate a ticket
    ticket_id = "TKT12345"
    encoded = generator.generate_qr_code(ticket_id, "sample_ticket.png")
    
    # Verify the ticket
    is_valid, message = verifier.verify_composite_qr("sample_ticket.png")
    print(f"Verification result: {message}")
    
    # Try to verify same ticket again
    is_valid, message = verifier.verify_composite_qr("sample_ticket.png")
    print(f"Second verification: {message}")
