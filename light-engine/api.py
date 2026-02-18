import uvicorn
import multiprocessing
import os
import sys
import io

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ensure modules directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
modules_path = os.path.join(current_dir, "modules")
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)

from API.app import app

if __name__ == "__main__":
    # Required for multiprocessing in frozen apps
    multiprocessing.freeze_support()
    
    # Run the uvicorn server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
