#!/bin/bash

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# clone and install modified version of orfipy -> added into requirements.txt
# git clone https://github.com/Genereux-akotenou/orfipy
# cd orfipy
# pip install .
# cd ..
# rm -r orfipy

echo "Setup complete. Run UI and FastAPI backend separately."
