import os
import time
import secrets
import json
from ticket_generator import TicketGenerator
from ticket_verifier import TicketVerifier
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

def display_qr(filename, title=None):
    """Display a QR code image"""
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return
    
    img = plt.imread(filename)
    plt.figure(figsize=(8, 8))
    plt.imshow(img)
    plt.axis('off')
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.show()

def test_ticket(ticket_id, draw_date=None, ticket_price=None, draw_number=None):
    print(f"\nTesting: {ticket_id}")
    print("-" * 50)
    
    # Generate composite QR
    print(f"Generating composite QR for ticket {ticket_id}...")
    ticket_data = generator.generate_composite_qr(
        ticket_id,
        "test_qr.png",
        draw_date,
        ticket_price,
        draw_number
    )
    print(f"Generated ticket data: {json.dumps(ticket_data, indent=2)}")
    
    print("\nDisplaying composite QR code...")
    display_qr("test_qr.png", f"Composite QR Code for {ticket_id}")
    
    print("\nVerifying composite QR...")
    is_valid, result = verifier.verify_composite_qr("test_qr.png")
    
    print("\nVerification Result:")
    print(f"Is Valid: {is_valid}")
    print(f"Result: {result}")
    
    print("\nTrying to verify same ticket again...")
    is_valid, result = verifier.verify_composite_qr("test_qr.png")
    print(f"Is Valid: {is_valid}")
    print(f"Result: {result}")

def test_composite_qr():
    """Test the composite QR code system"""
    print("Testing Composite QR Code System\n\n")
    
    # Create secret key
    secret_key = secrets.token_bytes(32)
    
    # Initialize generator and verifier
    global generator
    global verifier
    generator = TicketGenerator(secret_key)
    verifier = TicketVerifier(secret_key)
    
    # Test valid ticket
    test_ticket("VALID1234", ticket_price=100)

    print("\nTesting: Premium Ticket")
    print("-" * 50)

    # Test premium ticket
    test_ticket("PREM5678", ticket_price=500, draw_number=42)

if __name__ == "__main__":
    test_composite_qr()
