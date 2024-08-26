FROM python:3.10-slim-bullseye

WORKDIR /app

COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt --no-cahe-dir

COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "image_uploader.py"]