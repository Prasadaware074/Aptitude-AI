import uvicorn
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting Multi-Agent Aptitude Preparation System API...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
