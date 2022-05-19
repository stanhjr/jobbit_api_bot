from multiprocessing import cpu_count

# Socket Path
bine = 'unix: /home/stan/BOTS/jobbit_api_bot/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/home/stan/BOTS/jobbit_api_bot/logs/access_log'
errorlog =  '/home/stan/BOTS/jobbit_api_bot/logs/error_log'