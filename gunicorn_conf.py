import os
from multiprocessing import cpu_count

from dotenv import load_dotenv

load_dotenv()

# bind
host = os.getenv('FAST_API_HOST')
port = os.getenv('FAST_API_PORT')
bind = f"{host}:{port}"

# Socket Path
bine = 'unix: /home/stan/BOTS/jobbit_api_bot/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'


# Logging Options
loglevel = 'debug'
accesslog = '/home/stan/BOTS/jobbit_api_bot/logs/access_log'
errorlog = '/home/stan/BOTS/jobbit_api_bot/logs/error_log'

#
# sudo /home/stan/BOTS/jobbit_api_bot/venv/bin/gunicorn -c gunicorn_conf.py fast_api:app
