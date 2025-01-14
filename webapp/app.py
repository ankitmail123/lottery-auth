from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
import json
import base64
from io import BytesIO
from PIL import Image
import time
from datetime import datetime, timedelta

# Get the absolute path of the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Add parent directory to path to import ticket modules
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from ticket_generator import TicketGenerator
from ticket_verifier import TicketVerifier

app = Flask(__name__)
CORS(app)

# Initialize generator and verifier with a fixed secret key
SECRET_KEY = b'your-secret-key-here'  # Change this in production
generator = TicketGenerator(SECRET_KEY)
verifier = TicketVerifier(SECRET_KEY)

@app.route('/')
def index():
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), path)

@app.route('/generate', methods=['POST'])
def generate_ticket():
    try:
        data = request.get_json()
        ticket_id = data.get('ticket_id')
        if not ticket_id:
            return jsonify({'error': 'Ticket ID is required'}), 400

        # Optional parameters
        draw_date = data.get('draw_date')
        ticket_price = data.get('ticket_price')
        draw_number = data.get('draw_number')

        # Create a BytesIO object to store the QR code
        qr_buffer = BytesIO()
        
        # Generate the QR code
        ticket_data = generator.generate_composite_qr(
            ticket_id,
            qr_buffer,
            draw_date,
            ticket_price,
            draw_number
        )
        
        # Get the QR code as base64
        qr_buffer.seek(0)
        qr_image = Image.open(qr_buffer)
        
        # Resize for 10x10mm at 300dpi
        # 300 dpi = 300 pixels per inch
        # 10mm = 0.3937 inches
        # Therefore, size = 0.3937 * 300 = 118 pixels
        target_size = int(0.3937 * 300)
        qr_image = qr_image.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Save as PNG with maximum quality
        output_buffer = BytesIO()
        qr_image.save(output_buffer, format='PNG', optimize=False, quality=100)
        qr_base64 = base64.b64encode(output_buffer.getvalue()).decode()

        return jsonify({
            'success': True,
            'qr_code': qr_base64,
            'ticket_data': ticket_data,
            'size_info': {
                'width_mm': 10,
                'height_mm': 10,
                'dpi': 300,
                'pixels': target_size
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify', methods=['POST'])
def verify_ticket():
    try:
        # Get the image file from the request
        if 'qr_image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['qr_image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Save the image temporarily
        temp_path = 'temp_qr.png'
        file.save(temp_path)
        
        # Verify the QR code
        is_valid, result = verifier.verify_composite_qr(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'result': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use port 5050 instead of default 5000
    app.run(debug=True, port=5050)
