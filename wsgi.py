import sys
import os

path = '/home/Altikrity/Robobod_ai' 
if path not in sys.path:
    sys.path.append(path)

from app import app as application
