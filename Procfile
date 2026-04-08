release: sh -c 'export PYTHONPATH="${PWD}/src" && cd sandbox && python manage.py migrate --noinput && python manage.py collectstatic --noinput'
web: sh -c 'export PYTHONPATH="${PWD}/src" && cd sandbox && exec gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-file -'
