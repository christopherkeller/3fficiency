kill `cat /var/webapps/3fficiency/threefficiency/three.pid`
gunicorn_django -w 1 -D -b 0.0.0.0:8000 -p /var/webapps/3fficiency/threefficiency/three.pid /var/webapps/3fficiency/threefficiency/settings.py
