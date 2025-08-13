#!/bin/bash
cd /home/deandont/geo_monitoring_bot
source venv/bin/activate
pip freeze > requirements.txt
pip-audit -r requirements.txt >> logs/audit.log 2>&1
echo "--------------------------" >> logs/audit.log
