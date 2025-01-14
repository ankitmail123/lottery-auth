FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY webapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY webapp/ .
COPY ticket_generator.py .
COPY ticket_verifier.py .

# Expose port
EXPOSE 8080

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
