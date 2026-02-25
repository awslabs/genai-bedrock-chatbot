FROM public.ecr.aws/lambda/python:3.13
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir \
    --no-deps llama-index-embeddings-bedrock==0.7.3 llama-index-llms-bedrock==0.4.2 llama-index-llms-anthropic==0.8.0 && \
    pip install --no-cache-dir -r requirements.txt
COPY . ${LAMBDA_TASK_ROOT}
CMD ["genai_chat_app.lambda_handler"]
USER 1001
HEALTHCHECK --interval=600s --timeout=2s --retries=12 \
    CMD ["cat", "requirements.txt"]
