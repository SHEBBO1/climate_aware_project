# Climate-Aware Cloud AI for Farming (Full Project)

This project is a full prototype including:
- Flask API + GUI
- NOAA dataset upload & fetch (requires NOAA_TOKEN)
- Training pipeline (train.py) producing model.pkl
- IoT simulator
- Dockerfile & docker-compose for containerized deployment
- aws_deploy.sh to push Docker image to AWS ECR (skeleton to continue to ECS Fargate)

## Quickstart (local)

1. Create virtualenv and install deps:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. (Optional) Train model locally:
   ```bash
   python train.py
   ```

3. Run the app:
   ```bash
   python app.py
   ```
   Visit http://localhost:5000

## Docker

   docker build -t climate_farm_cloud .
   docker run -p 5000:5000 climate_farm_cloud

Or use docker-compose:
   docker-compose up --build

## NOAA Integration
- To fetch NOAA data via API set `NOAA_TOKEN` environment variable:
   export NOAA_TOKEN=your_token
- Use the GUI to fetch or upload NOAA CSVs and generate stats.

## AWS Deployment (ECS Fargate)
- Ensure AWS CLI is configured (`aws configure`).
- Run: `./aws_deploy.sh` to push image to ECR.
- Use AWS Console or IaC (CloudFormation / Terraform) to create ECS Task Definition, Service, and Application Load Balancer pointing to the image pushed to ECR.

## Files
See the repository for `app.py`, `train.py`, `data_fetcher.py`, `iot_simulator.py`, `Dockerfile`, `docker-compose.yml`, `aws_deploy.sh`, and templates/static assets.
