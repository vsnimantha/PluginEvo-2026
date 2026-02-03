from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import uvicorn
import threading
from Config.global_config import config

app = FastAPI()

@app.post("/report")
async def request_coverage_report(report: dict):
#TODO: Implement, coverage repor densing part
    pass

@app.get("/compile_and_generate_coverage")
async def compile_and_generate_coverage():
#TODO: Implement, coverage report generation part   
    pass


    


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

    start_server()


if __name__ == "__main__":
    main()
    
# python3 -m Feedback_Manager.feedback_server 