#!/usr/bin/env bash
set -euo pipefail
REPO_NAME="climate-farm-cloud"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text 2>/dev/null || true)"
TAG="${1:-latest}"
if [ -z "$ACCOUNT_ID" ]; then
  echo "AWS not configured or not authenticated. Configure AWS CLI first."
  exit 1
fi
IMAGE="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${TAG}"
echo "Building Docker image..."
docker build -t ${REPO_NAME}:${TAG} .
echo "Logging into ECR..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
echo "Create repo if not exists..."
aws ecr describe-repositories --repository-names ${REPO_NAME} --region ${REGION} >/dev/null 2>&1 || aws ecr create-repository --repository-name ${REPO_NAME} --region ${REGION}
echo "Tagging and pushing..."
docker tag ${REPO_NAME}:${TAG} ${IMAGE}
docker push ${IMAGE}
echo "Image pushed: ${IMAGE}"
echo "NOTE: This script uploads image to ECR. Next steps (create ECS task definition, service, ALB) require additional commands or use the AWS Console/CloudFormation/terraform."
