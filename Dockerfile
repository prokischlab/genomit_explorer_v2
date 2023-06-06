FROM tiangolo/python3.9

COPY . /app
ENV APP_HOME /app

WORKDIR $APP_HOME
COPY . ./

RUN pip install --upgrade pip==23.1.2
RUN pip install -r requirements.txt

EXPOSE $PORT

CMD waitress-serve --port=1040 --call hello:create_app
#CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --preload --timeout 0 --threads 8 app:app