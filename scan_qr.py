import cv2
import numpy as np
from pyzbar.pyzbar import decode
from ticket_verifier import TicketVerifier
from ticket_generator import TicketGenerator

def scan_qr(image_path):
    # Read the image
    image = cv2.imread(image_path)
    
    # Scan for QR codes
    decoded_objects = decode(image)
    
    if not decoded_objects:
        print("No QR code found in image")
        return
    
    # Get the data from the first QR code
    qr_data = decoded_objects[0].data.decode('utf-8')
    print(f"QR Code Data Length: {len(qr_data)} characters")
    
    # Create verifier with same key as generator
    generator = TicketGenerator()
    verifier = TicketVerifier(generator.secret_key)
    
    # Verify the ticket
    is_valid, message = verifier.verify_ticket(qr_data)
    print(f"\nVerification Result: {message}")

if __name__ == "__main__":
    print("Scanning actual size QR code:")
    scan_qr("ticket_qr_actual_size.png")
    
    print("\nScanning large QR code:")
    scan_qr("ticket_qr_large.png")
