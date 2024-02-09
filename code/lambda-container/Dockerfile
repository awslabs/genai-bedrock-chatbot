FROM public.ecr.aws/lambda/python:3.11@sha256:2012f94e9d0ce35d9c0d9e39f65832a483e0254273c58ab4532c847c0bdc9c2b
RUN yum update --security -y && yum clean all
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt --no-cache-dir
COPY . ${LAMBDA_TASK_ROOT}
CMD ["genai_chatbot.lambda_handler"]
USER 1001
HEALTHCHECK --interval=600s --timeout=2s --retries=12 \
    CMD ["cat", "requirements.txt"]