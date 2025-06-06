#!/bin/bash

# exit if any command fails
set -e

# pull latest changes from the repository
echo "pulling latest changes.."
git reset --hard -q HEAD
git pull -q origin main

# activating the virtual environment
echo "activating virtual environment.."
source .venv/bin/activate

# install dependencies
echo "installing dependencies.."
python -m pip install -r req.txt -q

# run the bot
echo "starting the api.."
exec .venv/bin/uvicorn main:app