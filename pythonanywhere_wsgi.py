"""
WSGI configuration for PythonAnywhere deployment.

INSTRUCTIONS:
1. Go to PythonAnywhere Web tab
2. Add a new web app
3. Choose "Manual configuration" (Python 3.10 or later)
4. In the WSGI configuration file, replace the contents with this file
5. Update the paths below to match your PythonAnywhere username

IMPORTANT: Replace 'YOUR_USERNAME' with your actual PythonAnywhere username
"""

import os
import sys

# Replace 'YOUR_USERNAME' with your PythonAnywhere username
path = '/home/YOUR_USERNAME/alx_travel_app_0x03'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# Load environment variables from .env file
from pathlib import Path
import environ

env = environ.Env()
environ.Env.read_env(os.path.join(path, '.env'))

# Initialize Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
