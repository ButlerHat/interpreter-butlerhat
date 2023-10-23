"""
API for interpeter.
"""
import os
import argparse
import tempfile
import uuid
from robot.api import logger
from typing	import Optional
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from interpreter import InterpreterManager
# Import your interpreter and other required modules here



parser = argparse.ArgumentParser(description="API for interpreter.")
parser.add_argument("--max_interpreters", type=int, default=1, 
                    help="Maximum number of interpreters that can be run simultaneously.")
args = parser.parse_args()
app = FastAPI()

interpreters = InterpreterManager(args.max_interpreters)
INTERPERTER_ID = interpreters.start_interpreter()
COOKIES_DIR = "/tmp/cookies/cookies"
STATE_JSON = "/tmp/cookies/cookies.json"

def setup():
    """    
    Only one interpreter is allowed to run at a time
    Load Keywords from gpt4.robot. Start browser
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, os.sep.join(["..", "apis", "gpt4v", "gpt4v.robot"])), "r", encoding='utf-8') as f:
        robot_code = f.read()
    # Get *** Settings *** section
    settings_section = robot_code.split("*** Settings ***")[1].split("***")[0]
    settings_section = "*** Settings ***\n" + settings_section
    result = interpreters.evaluate(INTERPERTER_ID, settings_section)

    # Get *** Keywords *** section
    keywords_section = robot_code.split("*** Keywords ***")[1].split("***")[0]
    keywords_section = "*** Keywords ***\n" + keywords_section
    result = interpreters.evaluate(INTERPERTER_ID, keywords_section)

    # Add *** Variables *** section
    variables_section = "*** Variables ***\n" + \
                        "${COOKIES_DIR}  " + f"{COOKIES_DIR}\n"
    interpreters.evaluate(INTERPERTER_ID, variables_section)

    # Start browser
    result = interpreters.evaluate(INTERPERTER_ID, f"Create Chat with cookies  {STATE_JSON}")
    logger.console(f"Open Browser if not exists: {result['stdout']}")

def _clear_interpreter_stdout(interpreter_id: str):
    stream_stdout = interpreters.get_info(interpreter_id).stream_stdout
    stream_stdout.truncate(0)
    stream_stdout.seek(0)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/start_browser_cookies/")
async def start_browser_cookies(cookie_file: UploadFile = File(...)):
    """
    Start browser with cookies.json
    """
    # Verify that the uploaded file is a .json
    if not cookie_file.filename or not cookie_file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="No file name found or not ended with .json. Need to upload a .json file.")
    
    # Create a temporary file. Create /tmp/cookies if not exists
    if not os.path.exists(os.sep.join(STATE_JSON.split(os.sep)[:-1])):
        os.makedirs(os.sep.join(STATE_JSON.split(os.sep)[:-1]))
        
    with open(STATE_JSON, "wb") as buffer:
        data = await cookie_file.read()  # Read file data
        buffer.write(data)  # Write data to specified file

    # Start browser
    try:
        result: dict = interpreters.evaluate(INTERPERTER_ID, f"Create Chat with cookies  {STATE_JSON}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot open ChatGPT. Try opening with cookies.json. Detail: {e}") from e
    logger.console(f"Open Browser if not exists: {result}")
    if not result['success']:
        raise HTTPException(status_code=400, detail=f"Cannot open ChatGPT. Try opening with cookies.json. Detail message: {result['message']}. Result: {str(result.get('result', ''))}")


@app.post("/generate")
async def generate(prompt: str = Form(...), image: Optional[UploadFile] = File(None)):
    """
    Evaluate the command in the interpreter with the given id.
    """
    # Open browser if not exists
    try:
        result: dict = interpreters.evaluate(INTERPERTER_ID, f"Open Browser if not exists  {STATE_JSON}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot open ChatGPT. Try opening with cookies.json. Detail: {e}") from e
    logger.console(f"Open Browser if not exists: {result}")
    if not result['success']:
        raise HTTPException(status_code=400, detail=f"Cannot open ChatGPT. Try opening with cookies.json. Detail message: {result['message']}. Result: {str(result.get('result', ''))}")

    # Add image to chat
    if image:
        temp_path = ""
        file_ext = f".{image.filename.split('.')[-1]}" if image.filename else ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp:
            data = await image.read()  # Read image data
            temp.write(data)  # Write to temporary file
            temp_path = temp.name  # Get the temporary file path
        try:
            result = interpreters.evaluate(INTERPERTER_ID, f"Upload image  {temp_path}")
            logger.console(f"Upload image: {result}")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Cannot upload image") from e
        finally:
            os.remove(temp_path)
    
    # Generate text
    try:
        result: dict = interpreters.evaluate(INTERPERTER_ID, f"${{message}}  Send Message  {prompt}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot generate text. Detail: {e}") from e
    logger.console(f"Send Message: {result}")
    if not result['success']:
        raise HTTPException(status_code=400, detail=f"Cannot generate text. Detail message: {result['message']}. Result: {str(result.get('result', ''))}")
    
    # Create unique id to identify the logging file
    logging_id: str = str(uuid.uuid4())
    _clear_interpreter_stdout(INTERPERTER_ID)
    result = interpreters.evaluate(INTERPERTER_ID, f"Log To Console  <{logging_id}>${{message}}<{logging_id}>")
    # Get the string of the log with the given id
    raw_gpt4_message = interpreters.get_info(INTERPERTER_ID).stream_stdout.getvalue()

    # Remove the log with the given id
    gpt4_message = raw_gpt4_message.split(f"<{logging_id}>")[1].split(f"<{logging_id}>")[0]
    gpt4_message = gpt4_message.split("ChatGPT\n\n")[1]

    return gpt4_message
    

@app.post("/delete_last_chat")
async def stop_interpreter():
    """
    Stop the interpreter with the given id.
    """
    try:
        result: dict = interpreters.evaluate(INTERPERTER_ID, "Reload ChatGPT")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot delete last chat. Detail: {e}") from e
    logger.console(f"Remove current chat: {result}")
    if not result['success']:
        raise HTTPException(status_code=400, detail=f"Cannot delete last chat. Detail message: {result['message']}. Result: {str(result.get('result', ''))}")
    

if __name__ == "__main__":
    import uvicorn
    setup()
    uvicorn.run(app, host="0.0.0.0", log_level="info")   # type: ignore
