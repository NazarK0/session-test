FROM python:3.13-bookworm
WORKDIR /code
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
WORKDIR /code/app
COPY . .
CMD ["fastapi", "run", "main.py", "--port", "80"]