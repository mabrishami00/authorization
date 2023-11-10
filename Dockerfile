FROM python:3.11.6-bullseye

WORKDIR /code

COPY ./app /code/

COPY requirements.txt /code/

ENV PYTHONBUFFERED=1

RUN pip install -r requirements.txt

EXPOSE 8002

CMD [ "python", "main.py" ]


