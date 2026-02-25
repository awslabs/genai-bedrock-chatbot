# GenAI Chat Assistant on AWS

## Introduction

This demo Chat Assistant application centers around the development of an advanced Chat Assistant using Amazon Bedrock and AWS's serverless GenAI solution. The solution demonstrates a Chat Assistant that utilizes the knowledge of the [Amazon SageMaker Developer Guide](https://docs.aws.amazon.com/sagemaker/latest/dg/gs.html?icmpid=docs_sagemaker_lp/index.html) and [SageMaker instance pricing](https://aws.amazon.com/sagemaker/pricing/). This Chat Assistant serves as an example of the power of Amazon Bedrock in processing and utilizing complex data sets, and its capability of converting natural language into Amazon Athena queries. It employs open source tools like LangChain and LlamaIndex to enhance its data processing and retrieval capabilities. The solution integrates various AWS resources, including Amazon S3 for storage, Amazon Kendra as vector store to support the retrieval augmented generation (RAG), AWS Glue for data preparation, Amazon Athena for efficient querying, Amazon Lambda for serverless computing, and Amazon ECS for container management. These resources collectively enable the Chat Assistant to effectively retrieve and manage content from documents and databases, illustrating the potential of Amazon Bedrock in sophisticated Chat Assistant applications.

### Models

The application uses the following Amazon Bedrock models via [global cross-region inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) for enhanced throughput and availability:

| Use Case | Model | Inference Profile ID |
|----------|-------|---------------------|
| Intent Classification | Claude Haiku 4.5 | `global.anthropic.claude-haiku-4-5-20251001-v1:0` |
| RAG & Agent | Claude Sonnet 4.6 | `global.anthropic.claude-sonnet-4-6` |
| SQL/Pricing Queries | Claude Sonnet 4.6 | `global.anthropic.claude-sonnet-4-6` |
| Embeddings | Amazon Titan Text Embeddings V2 | `amazon.titan-embed-text-v2:0` |

### Deployment

Please refer to this APG article for detailed deployment steps:
[Develop advanced generative AI chat-based assistants by using RAG and ReAct prompting](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/develop-advanced-generative-ai-chat-based-assistants-by-using-rag-and-react-prompting.html#develop-advanced-generative-ai-chat-based-assistants-by-using-rag-and-react-prompting-epics).

For a chat-assistant solution using Agents for Amazon Bedrock, please refer:

1. APG article: [Develop a fully automated chat-based assistant by using Amazon Bedrock agents and knowledge bases](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/develop-a-fully-automated-chat-based-assistant-by-using-amazon-bedrock-agents-and-knowledge-bases.html)
2. Github Repo: [genai-bedrock-agent-chat-assistant](https://github.com/awslabs/genai-bedrock-agent-chat-assistant/)

### Prerequisites

- Docker
- AWS CDK Toolkit 2.240.0+, installed and configured. For more information, see [Getting started with the AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) in the AWS CDK documentation.
- Python 3.13+, installed and configured. For more information, see Beginners Guide/Download in the Python documentation.
- An [active AWS account](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-creating.html)
- An [AWS account bootstrapped](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) by using AWS CDK in us-east-1.
- Enable Claude Haiku 4.5, Claude Sonnet 4.6, and Amazon Titan Text Embeddings V2 model access in the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/).

### Target technology stack

- Amazon Bedrock (Claude Haiku 4.5, Claude Sonnet 4.6, Titan Embeddings V2)
- Amazon ECS
- AWS Glue
- AWS Lambda
- Amazon S3
- Amazon Kendra
- Amazon Athena
- Elastic Load Balancer

### Target Architecture

![Architecture Diagram](assets/diagrams/architecture.png)

### Code

The code repository contains the following files and folders:

- `assets` folder – Static assets like architecture diagram, public dataset, etc.
- `code/lambda-container` folder – Python code for the Lambda function (LangChain, LlamaIndex, Bedrock integration)
- `code/streamlit-app` folder – Python code for the Streamlit container image running in ECS
- `tests` folder – Unit tests for the AWS CDK constructs
- `code/code_stack.py` – AWS CDK construct for creating all AWS resources
- `app.py` – AWS CDK stack entry point for deployment
- `requirements.txt` – Python dependencies for AWS CDK
- `requirements-dev.txt` – Python dependencies for running the unit test suite
- `cdk.json` – CDK configuration and context values

### Key Dependencies

| Component | Package | Version |
|-----------|---------|---------|
| Infrastructure | `aws-cdk-lib` | 2.240.0 |
| LLM Integration | `langchain-aws` | 1.3.0 |
| LLM Framework | `langchain` | 1.2.10 |
| Agent Orchestration | `langgraph` | 1.0.9 |
| SQL Query Engine | `llama-index-core` | 0.13.0 |
| Frontend | `streamlit` | 1.54.0 |

**Note:** The AWS CDK code uses [L3 constructs](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) and [AWS managed IAM policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html#aws-managed-policies) for deploying the solution.

## Useful commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.
