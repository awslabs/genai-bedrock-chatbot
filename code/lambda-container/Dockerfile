FROM public.ecr.aws/lambda/python:3.11@sha256:502afe114ba492ff1819826d8e9a6d86b03d002b7944813a06ff9cf1db9c9f0c
RUN yum update --security -y && yum clean all
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt --no-cache-dir
COPY . ${LAMBDA_TASK_ROOT}
CMD ["genai_chatbot.lambda_handler"]
USER 1001
HEALTHCHECK --interval=600s --timeout=2s --retries=12 \
    CMD ["cat", "requirements.txt"]