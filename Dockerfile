FROM ubuntu:16.04
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y -q python3-all python3-pip python3-dev gunicorn3
ADD ./requirements.txt /tmp/requirements.txt
RUN pip3 install -qr /tmp/requirements.txt
ADD . /opt/webapp/
WORKDIR /opt/webapp/
CMD [ "gunicorn3", "app.app:app", "-b", "0.0.0.0:8000" ]
