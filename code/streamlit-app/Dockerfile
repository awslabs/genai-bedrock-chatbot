FROM python:3.11@sha256:a87accdfc2fd5cca7e2ffeabb5c32749b932bc3d1e5a25c3b6adc0c26af7fce8
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir
COPY *.py ./
EXPOSE 8501
HEALTHCHECK --interval=600s --timeout=2s --retries=12 \
    CMD ["curl", "-f", "http://localhost:8501/"]
ENTRYPOINT ["streamlit", "run", "app.py", "--server.headless", "true", "--browser.serverAddress='0.0.0.0'", "--browser.gatherUsageStats", "false"]
USER 1001