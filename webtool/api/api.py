# ---------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from uuid import uuid4
from pydantic import BaseModel
import asyncio
import shutil
from pathlib import Path
import logging
import json, os
import threading
import queue
from dotenv import load_dotenv
load_dotenv()

APP_STATE_DIR = Path("./__files__/tasks")
APP_STATE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR = Path("./__files__/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path("./__files__/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

API_PROD_URL = os.getenv("API_PROD_URL", "http://127.0.0.1:8000")
TASKS_FILE = Path("./__files__/tasks/tasks_checkpoint.json")

logging.basicConfig(
    filename="__files__/api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ---------------------------------------------------------------
# MODEL INFERENCE UTILS
# ---------------------------------------------------------------
from core import AnnotatorPipeline

# ---------------------------------------------------------------
# INIT API
# ---------------------------------------------------------------
# 1. queue & task storage
job_queue = queue.Queue()
tasks = {}
cancel_requested = set()
# 2. api
app = FastAPI(
    title="GeneLM Webtool",
    description="GeneLM Webtool is a web application that allows you to annotate Bacterial Genomes with Transformer Models.",
    version="0.0.1",
    contact={
        "name": "UM6P BIOINFORMATICS LAB",
        "url": "https://bioinformatics.um6p.ma/",
        "email": "bioinformatics@um6p.ma"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)
# 3. annotation model
annotator = AnnotatorPipeline()

# ---------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------
def save_tasks():
    with TASKS_FILE.open("w") as f:
        json.dump(tasks, f)

def load_tasks():
    global tasks
    if TASKS_FILE.exists():
        with TASKS_FILE.open("r") as f:
            try:
                tasks = json.load(f)
            except json.JSONDecodeError:
                logging.error("Error loading tasks.json, resetting tasks.")
                tasks = {}

def worker():
    """Continuously processes tasks from the queue in sequence."""
    global current_task_uuid
    global job_queue
    
    while True:
        try: 
            task_uuid, file_path, output_format = job_queue.get()
            
            # if task was canceled before execution
            if task_uuid in cancel_requested:
                logging.info(f"Task {task_uuid} was canceled before execution. Skipping.")
                cancel_requested.remove(task_uuid)
                # job_queue.task_done()
                continue
            
            logging.info(f"Processing task {task_uuid} - File: {file_path} - Format: {output_format}")

            tasks[task_uuid]["status"] = "Processing"
            tasks[task_uuid]["progress"] = 1
            tasks[task_uuid]["result"] = ""
            tasks[task_uuid]["exec_state"] = {}
            save_tasks()

            current_task_uuid = task_uuid
            
            try:
                result_path = annotator.pipeline(file_path, output_format, tasks, task_uuid, logging)
                if task_uuid in cancel_requested:
                    logging.info(f"Task {task_uuid} was canceled during execution. Stopping.")
                    cancel_requested.remove(task_uuid)
                    tasks[task_uuid]["status"] = "Canceled"
                    tasks[task_uuid]["progress"] = 100
                    save_tasks()
                    continue
                save_tasks()
                logging.info(f"Task {task_uuid} completed - Result: {result_path}")
            except Exception as e:
                logging.error(f"Error while processing task {task_uuid}: {str(e)}")
            
            current_task_uuid = None
            job_queue.task_done()
        except Exception as e:
            logging.error(f"Error while processing task {task_uuid}: {str(e)}")
# ---------------------------------------------------------------
# ON STARTUP
# ---------------------------------------------------------------
load_tasks()
threading.Thread(target=worker, daemon=True).start()

# ---------------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------------
@app.post("/tis/get-annotation")
async def submit_annotation(file: UploadFile = File(...), output_format: str = "GFF", background_tasks: BackgroundTasks = None):
    """Submits an annotation request and adds it to the job queue."""
    allowed_formats = {"GFF", "CSV"}
    if output_format.upper() not in allowed_formats:
        raise HTTPException(status_code=400, detail="Invalid output format. Choose 'CSV' or 'GFF'.")

    allowed_extensions = {".fasta", ".fna"}
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    task_uuid = str(uuid4())
    file_path = Path(f"./__files__/uploads/{task_uuid}_{file.filename}")

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    tasks[task_uuid] = {"status": "Queued", "progress": 0, "result": None, "exec_state": {}}
    save_tasks()

    background_tasks.add_task(job_queue.put, (task_uuid, file_path, output_format))

    logging.info(f"Task {task_uuid} submitted - File: {file.filename} - Format: {output_format}")
    return {"uuid": task_uuid, "message": "Task submitted. Use /tis/get-progress/{uuid} to check status."}

@app.get("/tis/get-progress/{uuid}")
async def get_progress(uuid: str):
    if uuid not in tasks:
        logging.warning(f"Progress check failed - Task {uuid} not found")
        raise HTTPException(status_code=404, detail="Task not found")
    
    logging.info(f"Progress check - Task {uuid} - Status: {tasks[uuid]['status']} - Progress: {tasks[uuid]['progress']}%")
    message = ""
    if not (tasks[uuid]["result"] != None and ("/" in tasks[uuid]["result"] or "..." in tasks[uuid]["result"])):
        message = tasks[uuid]["result"]
        
    return {
        "uuid": uuid,
        "status": tasks[uuid]["status"],
        "progress": tasks[uuid]["progress"],
        "message": message,
        "exec_state": tasks[uuid]["exec_state"]
    }

@app.get("/tis/download/{filename}", include_in_schema=False)
async def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.get("/tis/get-result/{uuid}")
async def get_result(uuid: str):
    if uuid not in tasks or tasks[uuid]["status"] != "Completed":
        logging.warning(f"Result retrieval failed - Task {uuid} not completed or found")
        raise HTTPException(status_code=404, detail="Result not available yet")

    result_path = Path(tasks[uuid]["result"])
    seq_id = tasks[uuid]["exec_state"]["seq_id"]
    if not result_path.exists():
        logging.warning(f"Result file missing - Task {uuid}")
        raise HTTPException(status_code=404, detail="Result file not found")

    # public URL to access file
    file_url = f"{API_PROD_URL}/tis/download/{result_path.name}"
    logging.info(f"Result retrieved - Task {uuid} - File URL: {file_url}")
    return {"uuid": uuid, "result_url": file_url, "seq_id": seq_id}

@app.delete("/tis/cancel-task/{uuid}")
async def cancel_task(uuid: str):
    global job_queue
    
    if uuid not in tasks:
        logging.warning(f"Cancel request failed - Task {uuid} not found")
        raise HTTPException(status_code=404, detail="Task not found")

    # if task is queued, remove it before execution (safely)
    new_queue = queue.Queue()
    while not job_queue.empty():
        task = job_queue.get()
        if task[0] != uuid:
            new_queue.put(task)
    job_queue = new_queue

    # if task is currently running, request cancellation
    if tasks[uuid]["status"] != "Canceled" or tasks[uuid]["status"] == "Processing":
        logging.warning(f"Canceling active task {uuid}. Stopping execution.")
        cancel_requested.add(uuid)
        tasks[uuid]["status"] = "Canceled"
        save_tasks()
    else:
        # remove from tasks if it was only in the queue
        del tasks[uuid]
        save_tasks()

    logging.info(f"Task {uuid} successfully canceled")
    return {"uuid": uuid, "message": "Task cancellation requested"}

