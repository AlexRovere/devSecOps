FROM python:3.12@sha256:df3b7c223e6fee2bd45166f5ebd3fd9d2c09d5e5f8b62b36f4c5d72fc63dc8a1
LABEL maintainer="Al Rov"
LABEL description="Image for python backend of Task Manager application"
LABEL version=1.0

WORKDIR /app
COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
