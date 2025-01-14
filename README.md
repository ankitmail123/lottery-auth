# Lottery Ticket QR Code Generator and Verifier

A secure system for generating and verifying lottery tickets using QR codes with both online and offline verification capabilities.

## Features

- Generate secure QR codes for lottery tickets
- Double QR verification (outer + inner)
- Timestamp-based validation
- HMAC security
- Web interface for ticket generation
- Mobile app for offline verification
- Print-ready QR codes (10x10mm at 300dpi)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the web application:
```bash
python app.py
```

3. Access the web interface at `http://localhost:8080`

## Mobile App

The mobile app is built with React Native and can be found in the `mobile-app` directory.

## Security Features

- Encrypted ticket data
- Inner QR code validation
- Timestamp verification
- Used ticket tracking
- Offline verification support
