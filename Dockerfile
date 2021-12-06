FROM python:3.9.9
COPY ./requirements.txt /tmp/
COPY ./EstropadakParser-0.1.13.tar.gz /tmp/
# RUN apt-get update 
ADD . /opt/webapp/
WORKDIR /opt/webapp/
RUN pip install gunicorn
# RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install /tmp/EstropadakParser-0.1.13.tar.gz
RUN pip install -r /tmp/requirements.txt
CMD [ "gunicorn", "app.app:app", "-b", "0.0.0.0:8000" ]
