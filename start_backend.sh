#!/bin/bash
cd /home/souhail/projectss/omnianalyse/backend
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload