import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable

settings_module = 'Unitech.deployment' if 'WEBSITE_HOSTNAME' in os.environ else 'Unitech.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

# Initialize Django
django.setup()

# Attempt to connect to the database
from django.db import connections
try:
    connections["default"].connect()
    print("Database connection successful")
except Exception as e:
    print(f"Database connection error: {str(e)}")