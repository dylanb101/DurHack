
# If Beginning to Develop
Run the commands below before first starting the backend server.


python3 -m venv venv  # Create the virtual environment
source venv/bin/activate # Activate it
pip install -r requirements.txt # Install dependencies

# To run the Backend locally
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Put installed packages into requirements
Need to be in the virtual env
pip freeze > requirements.txt