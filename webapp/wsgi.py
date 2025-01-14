import os
import sys

# Add the application directory to the Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

# Add the parent directory to the Python path (for ticket_generator and ticket_verifier)
parent_dir = os.path.dirname(app_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from app import app as application
