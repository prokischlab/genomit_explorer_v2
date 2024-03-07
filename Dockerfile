FROM python:3.9-slim-buster

ENV DASH_DEBUG_MODE False
COPY . /app
ENV APP_HOME /app

WORKDIR $APP_HOME
COPY . ./

RUN pip install --upgrade pip==23.1.2
RUN pip install -r requirements.txt

EXPOSE $PORT

#CMD gunicorn --bind 0.0.0.0:$PORT app:server
CMD waitress-serve --port=$PORT app:server
#CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --preload --timeout 0 --threads 8 app:app