nohup uwsgi --http-socket :8083 --plugin python --wsgi-file __init__.py  --logto docker.log --callable app &