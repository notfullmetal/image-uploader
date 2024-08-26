FROM python:3.10-slim-bullseye

WORKDIR /app

COPY . .
RUN apt-get update && apt-get install \
--no-install-recommends \
-y curl build-essential

RUN pyhton3 -m pip install -r requirements.txt

EXPOSE 8000

CMD ["fastapi", "dev", "image_uploader.py"]