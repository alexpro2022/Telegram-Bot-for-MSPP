FROM python:3.11-slim

WORKDIR /app

COPY requirements requirements

RUN python -m pip install --upgrade pip && \ 
    pip install -r requirements/development.txt --no-cache-dir

COPY src .   

RUN chmod +x start.sh

CMD ["./start.sh"]

