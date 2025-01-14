from ticket_generator import TicketGenerator
import qrcode
from PIL import Image
import os

def mm_to_pixels(mm, dpi=300):
    """Convert millimeters to pixels at given DPI"""
    return int((mm / 25.4) * dpi)

def generate_small_qr(ticket_id, size_mm=10):
    # Initialize ticket generator
    generator = TicketGenerator()
    
    # Generate ticket data
    encoded_data = generator.generate_ticket_data(ticket_id)
    
    # Calculate size in pixels (at 300 DPI)
    size_pixels = mm_to_pixels(size_mm)
    
    # Create QR code with minimal size
    qr = qrcode.QRCode(
        version=1,  # Force minimum version
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Use lower error correction for smaller size
        box_size=1,  # Minimum box size
        border=1,    # Minimum border
    )
    
    # Add data
    qr.add_data(encoded_data)
    qr.make(fit=True)
    
    # Create image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Resize to exact dimensions
    qr_image = qr_image.resize((size_pixels, size_pixels), Image.Resampling.LANCZOS)
    
    # Save images at different scales for visualization
    qr_image.save("ticket_qr_actual_size.png")
    
    # Save a larger version for easy viewing
    large_size = mm_to_pixels(50)  # 50mm for visibility
    qr_image_large = qr_image.resize((large_size, large_size), Image.Resampling.LANCZOS)
    qr_image_large.save("ticket_qr_large.png")
    
    # Print information
    print(f"Generated QR code for ticket ID: {ticket_id}")
    print(f"Actual size (10mm x 10mm) saved as: ticket_qr_actual_size.png")
    print(f"Large preview (50mm x 50mm) saved as: ticket_qr_large.png")
    print(f"QR code contains {len(encoded_data)} characters of data")
    print(f"Actual image size: {size_pixels}x{size_pixels} pixels at 300 DPI")

if __name__ == "__main__":
    generate_small_qr("LOTTERY123")
