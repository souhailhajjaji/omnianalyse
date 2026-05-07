#!/bin/bash
cd /home/souhail/projectss/omnianalyse/venv
source bin/activate
cd /home/souhail/projectss/omnianalyse/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001