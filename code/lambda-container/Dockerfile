FROM public.ecr.aws/lambda/python:3.11@sha256:4c04b142654ce3d1b8d705880bf5c720599b5984fd4c751763f09f1682308490
RUN yum update --security -y && yum clean all
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt --no-cache-dir
COPY . ${LAMBDA_TASK_ROOT}
CMD ["genai_chat_app.lambda_handler"]
USER 1001
HEALTHCHECK --interval=600s --timeout=2s --retries=12 \
    CMD ["cat", "requirements.txt"]