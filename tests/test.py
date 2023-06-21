"""
Tests for the FastAPI app.
"""
import os
import sys
from fastapi.testclient import TestClient  # pylint: disable=import-error, wrong-import-position
# Add parent directory to path
current_file_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f"{current_file_path}/..")
sys.path.append(f"{current_file_path}/../src")
from src.app import app, Command, interpreters  # pylint: disable=import-error, wrong-import-position

client = TestClient(app)


def test_start_interpreter():
    """
    Test the start_interpreter endpoint.
    """
    response = client.get("/start_interpreter")
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert data['id'] in interpreters  # Assumes interpreter ids are stored in 'interpreters'


def test_evaluate():
    """
    Test the evaluate endpoint.
    """
    # Assuming the start_interpreter test has already been run
    response = client.get("/start_interpreter")
    interpreter_id = response.json()['id']

    cmd = Command(command="""
    *** Settings ***\nLibrary   ButlerRobot.AIBrowserLibrary  fix_bbox=${TRUE}  presentation_mode=${True}  console=${False}  record=${True}  output_path=${OUTPUT_DIR}/crawl_amazon_data  WITH NAME  Browser
    """)
    response = client.post(f"/evaluate/{interpreter_id}", json=cmd.dict())
    assert response.status_code == 200
    assert response.json().get("success", False), response.json().get("message", "No error message provided")

    response = client.post("/evaluate/non_existent_id", json=cmd.dict())
    assert response.status_code == 404


def test_stop_interpreter():
    """
    Test the stop_interpreter endpoint.
    """
    # Assuming the start_interpreter test has already been run
    response = client.get("/start_interpreter")
    interpreter_id = response.json()['id']

    response = client.delete(f"/stop_interpreter/{interpreter_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Interpreter stopped successfully."}

    assert interpreter_id not in interpreters  # Check that interpreter was removed

    response = client.delete("/stop_interpreter/non_existent_id")
    assert response.status_code == 404
