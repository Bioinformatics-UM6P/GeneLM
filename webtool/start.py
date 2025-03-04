import subprocess
import webbrowser
import time, sys, os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# backend
api_process = subprocess.Popen(["uvicorn", "--app-dir", "api", "api:app", "--host", "127.0.0.1", "--port", "8000"])
time.sleep(3)

# UI
ui_process = subprocess.Popen(["streamlit", "run", "ui/app.py"])
webbrowser.open("http://127.0.0.1:8501")

# keep processes running
try:
    api_process.wait()
    ui_process.wait()
except KeyboardInterrupt:
    api_process.terminate()
    ui_process.terminate()
