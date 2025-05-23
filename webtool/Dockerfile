FROM nvidia/cuda:12.2.0-base-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python3 -m venv venv && \
    ./venv/bin/pip install --upgrade pip && \
    ./venv/bin/pip install -r requirements.txt && \
    bash postinstall.sh || true

EXPOSE 8501 8502 8000

CMD ./venv/bin/streamlit run ui/app.py --server.headless true > ./api/__files__/streamlit.log 2>&1 & \
    ./venv/bin/uvicorn --app-dir api api:app --host 0.0.0.0 --port 8000 --reload
