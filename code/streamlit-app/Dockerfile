FROM python:3.11@sha256:47d0618fb878d93e1b8cacb184fd8f727ae95c1b85d5959723e1d3e1848e2aba
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir
COPY *.py ./
EXPOSE 8501
HEALTHCHECK --interval=600s --timeout=2s --retries=12 \
    CMD ["curl", "-f", "http://localhost:8501/"]
ENTRYPOINT ["streamlit", "run", "app.py", "--server.headless", "true", "--browser.serverAddress='0.0.0.0'", "--browser.gatherUsageStats", "false"]
USER 1001