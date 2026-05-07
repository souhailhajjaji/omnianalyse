#!/bin/bash
cd /home/souhail/projectss/omnianalyse/backend
source /home/souhail/projectss/omnianalyse/venv/bin/activate
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8001