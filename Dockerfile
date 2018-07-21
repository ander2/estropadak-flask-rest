FROM ubuntu:16.04
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y -q python3-all python3-pip python3-dev gunicorn3
ADD ./requirements.txt /tmp/
COPY ./EstropadakParser-0.1.2.tar.gz /tmp/
RUN pip3 install /tmp/EstropadakParser-0.1.2.tar.gz
RUN pip3 install -qr /tmp/requirements.txt
ADD . /opt/webapp/
WORKDIR /opt/webapp/
CMD [ "gunicorn3", "app.app:app", "-b", "0.0.0.0:8000" ]
