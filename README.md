# GenAI Chat Assistant on AWS

## Introduction

This demo Chat Assistant application centers around the development of an advanced Chat Assistant using Amazon Bedrock and AWS's serverless GenAI solution. The solution demonstrates a Chat Assistant that utilizes the knowledge of the [Amazon SageMaker Developer Guide](https://docs.aws.amazon.com/sagemaker/latest/dg/gs.html?icmpid=docs_sagemaker_lp/index.html) and [SageMaker instance pricing](https://aws.amazon.com/sagemaker/pricing/). This Chat Assistant serves as an example of the power of Amazon Bedrock in processing and utilizing complex data sets, and it’s capability of converting natural language into Amazon Athena queries. It employs open source tools like LangChain and LLamaIndex to enhance its data processing and retrieval capabilities. The article also highlights the integration of various AWS resources, including Amazon S3 for storage, Amazon Kendra as vector store to support the retrieval augmented generation (RAG), AWS Glue for data preparation, Amazon Athena for efficient querying, Amazon Lambda for serverless computing, and Amazon ECS for container management. These resources collectively enable the Chat Assistant to effectively retrieve and manage content from documents and databases, illustrating the potential of Amazon Bedrock in sophisticated Chat Assistant applications.

### Deployment

Please refer to this APG article for detailed deployment steps:
[Develop advanced generative AI chat-based assistants by using RAG and ReAct prompting](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/develop-advanced-generative-ai-chat-based-assistants-by-using-rag-and-react-prompting.html#develop-advanced-generative-ai-chat-based-assistants-by-using-rag-and-react-prompting-epics).

For a chat-assistant solution using Agents for Amazon Bedrock, please refer:

1. APG article: [Develop a fully automated chat-based assistant by using Amazon Bedrock agents and knowledge bases](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/develop-a-fully-automated-chat-based-assistant-by-using-amazon-bedrock-agents-and-knowledge-bases.html)
2. Github Repo: [genai-bedrock-agent-chat-assistant](https://github.com/awslabs/genai-bedrock-agent-chat-assistant/)

### Prerequisites

- Docker
- AWS CDK Toolkit 2.132.1+, installed installed and configured. For more information, see [Getting started with the AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) in the AWS CDK documentation.
- Python 3.11+, installed and configured. For more information, see Beginners Guide/Download in the Python documentation.
- An [active AWS account](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-creating.html)
- An [AWS account bootstrapped](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) by using AWS CDK in us-east-1. The us-east-1 AWS Region is required for Amazon Bedrock Claude and Amazon Titan Embedding model access.
- Enable Claude and Titan embedding model access in Bedrock service.

### Target technology stack

- Amazon Bedrock
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

- `assets` folder – The various static assets like architecture diagram, public dataset, etc are available here
- `code/lambda-container` folder– The Python code that is run in the Lambda function
- `code/streamlit-app` folder– The Python code that is run as the container image in ECS
- `tests` folder – The Python files that is run to unit test the AWS CDK constructs
- `code/code_stack.py` – The AWS CDK construct Python files used to create AWS resources
- `app.py` – The AWS CDK stack Python files used to deploy AWS resources in target AWS account
- `requirements.txt` – The list of all Python dependencies that must be installed for AWS CDK
- `requirements-dev.txt` – The list of all Python dependencies that must be installed for AWS CDK to run the unit test suite
- `cdk.json` – The input file to provide values required to spin up resources

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
