import os
import subprocess
import sys
import time
import webbrowser

def main():
    # Run the Flask app in the same Python environment.
    # Open the browser automatically for a polished demo experience.
    port = int(os.getenv("PORT", "5000"))
    process = subprocess.Popen([sys.executable, "app.py"])

    time.sleep(2)
    webbrowser.open(f"http://localhost:{port}/ideas")

    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    main()
