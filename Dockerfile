FROM python:3.7.2-slim
ENV PYTHONIOENCODING utf-8

COPY . /code/

RUN pip install flake8
RUN pip install  --upgrade --no-cache-dir --ignore-installed logging_gelf
RUN pip install  --upgrade --no-cache-dir --ignore-installed marketorestpython==0.5.25

RUN pip install -r /code/requirements.txt

WORKDIR /code/


CMD ["python", "-u", "/code/src/main.py"]
