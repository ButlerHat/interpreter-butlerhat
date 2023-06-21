"""
Example for using the API
"""
import json
import requests

# Base URL of the API
base_url = "http://localhost:8000"  # adjust this to the actual URL of your API

# Start an interpreter
response = requests.get(f"{base_url}/start_interpreter", timeout=5)
data = response.json()
interpreter_id = data['id']
print(f"Started interpreter with id {interpreter_id}")

# Send a command
command = """
*** Settings ***\nLibrary   ButlerRobot.AIBrowserLibrary  fix_bbox=${TRUE}  presentation_mode=${True}  console=${False}  record=${True}  output_path=${OUTPUT_DIR}/crawl_amazon_data  WITH NAME  Browser
"""
headers = {'Content-type': 'application/json'}
data = json.dumps({"command": command})
response = requests.post(f"{base_url}/evaluate/{interpreter_id}", data=data, headers=headers, timeout=5)
print(response.json())  # prints the result of the command execution

command = """
# Open Browser    https://www.google.com
Sleep  3
Scroll Down
AI.Click on accept cookies
"""
headers = {'Content-type': 'application/json'}
data = json.dumps({"command": command})
response = requests.post(f"{base_url}/evaluate/{interpreter_id}", data=data, headers=headers, timeout=180)
print(response.json())  # prints the result of the command execution


# Stop the interpreter
response = requests.delete(f"{base_url}/stop_interpreter/{interpreter_id}", timeout=5)
print(response.json())  # prints the result of the stop command
