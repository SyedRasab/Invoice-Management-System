import sys
import os

# Add the backend directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.append(project_home)

from app import app as application
