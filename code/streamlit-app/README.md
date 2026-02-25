# Streamlit Frontend UI Application

## Introduction

This application is the frontend UI for the GenAI Chat Assistant powered by Amazon Bedrock. The application is deployed in Amazon ECS (AWS Fargate) with an Application Load Balancer on port 8080.

## Component Details

#### Prerequisites

- All resources defined in the CDK stack deployed successfully
- Lambda function `chat-assistant-stack-chat-lambda` is running

#### Technology stack

- [Streamlit](https://streamlit.io/) 1.54.0
- [Amazon ECS](https://aws.amazon.com/ecs/) (Fargate, ARM64)
- [Application Load Balancer](https://aws.amazon.com/elasticloadbalancing/application-load-balancer/) (port 8080)
- Python 3.13

### Run Locally

```bash
export LAMBDA_FUNCTION_NAME=chat-assistant-stack-chat-lambda
export AWS_REGION=us-east-1
export LOG_LEVEL=INFO
streamlit run app.py --server.runOnSave true --server.port 8501
```

### User Interface

![UI](images/UI-FrontPage.png)
