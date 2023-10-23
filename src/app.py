"""
API for interpeter.
"""
import argparse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from fastapi.middleware.cors import CORSMiddleware
from interpreter import InterpreterManager
# Import your interpreter and other required modules here

# For test to work
interpreters = InterpreterManager(-1)
app = FastAPI()

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

class Command(BaseModel):
    """
    Command to be executed by the interpreter.
    """
    command: str

@app.get("/start_interpreter")
async def start_interpreter():
    """
    Start the RobotFramework interpreter.
    """
    assert interpreters is not None, "InterpreterManager not initialized"
    try:
        interpreter_id = interpreters.start_interpreter()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": interpreter_id}


@app.post("/evaluate/{interpreter_id}")
async def evaluate(interpreter_id: str, cmd: Command):
    """
    Evaluate the command in the interpreter with the given id.
    """
    assert interpreters is not None, "InterpreterManager not initialized"
    if interpreter_id not in interpreters:
        raise HTTPException(status_code=404, detail="Interpreter not found")
    try:
        # Execute the command
        result: dict = interpreters.evaluate(interpreter_id, cmd.command)
    except Exception as e:  # pylint: disable=broad-except
        return {"error": str(e)}
    print(result)
    return {
        "success": result['success'],
        "message": result['message'],
        "result": str(result.get('result', ""))
    }


@app.delete("/stop_interpreter/{interpreter_id}")
async def stop_interpreter(interpreter_id: str):
    """
    Stop the interpreter with the given id.
    """
    assert interpreters is not None, "InterpreterManager not initialized"
    if interpreter_id not in interpreters:
        raise HTTPException(status_code=404, detail="Interpreter not found")
    interpreters.stop_interpreter(interpreter_id)
    return {"message": "Interpreter stopped successfully."}


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="API for interpreter.")
    parser.add_argument("--max_interpreters", type=int, default=-1, 
                        help="Maximum number of interpreters that can be run simultaneously.")
    args = parser.parse_args()
    interpreters.set_max_interpreters(args.max_interpreters)

    uvicorn.run(app, host="0.0.0.0")  # type: ignore
