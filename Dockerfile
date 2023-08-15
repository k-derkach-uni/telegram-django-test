FROM python:3.9
WORKDIR .
COPY . .
EXPOSE 8000
RUN pip install pip --upgrade
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/cupervisord.conf

RUN python manage.py makemigrations
RUN python manage.py migrate
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/cupervisord.conf", "-n"]
