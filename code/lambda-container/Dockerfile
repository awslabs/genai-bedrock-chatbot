FROM public.ecr.aws/lambda/python:3.11@sha256:accf44b337d70ef4be18d4e864539881c4bc6274efe88a4772c47b5977b79cf6
RUN yum update --security -y && yum clean all
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt --no-cache-dir
COPY . ${LAMBDA_TASK_ROOT}
CMD ["genai_chatbot.lambda_handler"]
USER 1001
HEALTHCHECK --interval=600s --timeout=2s --retries=12 \
    CMD ["cat", "requirements.txt"]