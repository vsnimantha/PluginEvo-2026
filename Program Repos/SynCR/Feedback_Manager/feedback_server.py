from fastapi import FastAPI, HTTPException
import requests
import uvicorn
import threading
import Program_Generator.program_generator_tmpl as program_generator_tmpl
from Config.global_config import config

app = FastAPI()

def analyze_coverage_report(report):
    """
    Analyzes the coverage report and decides how to improve the code.
    """
    if report and "coverage" in report:
        coverage = report["coverage"]
        print(f"Coverage Report: {coverage}%")
        if coverage < 90:  # Example threshold
            print("Coverage is low. Improving code...")
        else:
            print("Coverage is sufficient.")
    else:
        print("Invalid coverage report received.")

@app.post("/report")
async def receive_report(report: dict):
    """
    API endpoint to receive the coverage report from App B.
    """
    print("Received coverage report from App B.")
    analyze_coverage_report(report)
    return {"status": "Report received"}

def start_server():
    """
    Starts the FastAPI server for App A.
    """
    uvicorn.run(app, host=config.FEEDBACK_MANAGER.server_host, port=config.FEEDBACK_MANAGER.server_port)
    # uvicorn.run(app, host="0.0.0.0", port=5002)

def main():
    """
    Main loop for App A.
    """
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

if __name__ == "__main__":
    # main()
    pass
# python3 -m Feedback_Manager.feedback_server 