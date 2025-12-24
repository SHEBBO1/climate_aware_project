# Deploying Climate-Aware Cloud AI for Farming on Kubernetes

## 1. Project Overview

This document explains step by step how to download, deploy, and run the Climate-Aware Cloud AI for Farming project on a Kubernetes cloud environment .

The system is a **Flask-based AI application** that:

* Uses Machine Learning for irrigation decision support
* Integrates climate data (NOAA)
* Runs inside Docker containers
* Is deployed on Kubernetes for scalability, fault tolerance, and cloud readiness

---

 2. Download the Project Source Code

Option 1: Clone from GitHub

```bash
git clone https://github.com/USERNAME/climate-farm-cloud.git
cd climate-farm-cloud
```

 Option 2: Download ZIP

1. Download the project as a ZIP file
2. Extract it
3. Open the project folder in Terminal

---

 3. Test the Application Locally Using Docker

Before deploying to Kubernetes, the Docker image must work correctly.

Build the Docker Image

```bash
docker build -t climate-farm-cloud .
```

 Run the Container

```bash
docker run -p 5000:5000 climate-farm-cloud
```

Test in Browser

```
http://localhost:5000
```

If the application works locally, it is ready for Kubernetes deployment.

---

 4. Push Docker Image to a Container Registry

Kubernetes pulls images from a **container registry** such as Docker Hub or AWS ECR.

Example Using Docker Hub

 Login to Docker Hub

```bash
docker login
```

 Tag the Image

```bash
docker tag climate-farm-cloud yourusername/climate-farm-cloud:latest
```

 Push the Image

```bash
docker push yourusername/climate-farm-cloud:latest
```

---

 5. Set Up Kubernetes Cluster

 Option A: Local Cluster (Minikube)

```bash
minikube start
kubectl get nodes
```

Option B: Cloud Cluster (AWS EKS / GKE / AKS)

1. Create the cluster from the cloud console
2. Configure kubectl
3. Verify connection:

```bash
kubectl get nodes
```

---

6. Create Kubernetes Deployment

Create a file named `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: climate-farm-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: climate-farm
  template:
    metadata:
      labels:
        app: climate-farm
    spec:
      containers:
      - name: climate-farm-container
        image: yourusername/climate-farm-cloud:latest
        ports:
        - containerPort: 5000
        env:
        - name: NOAA_TOKEN
          value: "your_noaa_token"
```

Apply the deployment:

```bash
kubectl apply -f deployment.yaml
```

Check pod status:

```bash
kubectl get pods
```

---

 7. Expose the Application Using a Service

Create a file named `service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: climate-farm-service
spec:
  type: NodePort
  selector:
    app: climate-farm
  ports:
  - port: 80
    targetPort: 5000
    nodePort: 30007
```

Apply the service:

```bash
kubectl apply -f service.yaml
kubectl get svc
```

---

8. Access the Application

If Using Minikube

```bash
minikube service climate-farm-service
```

 If Using Cloud Kubernetes

Open in browser:

```
http://<Node-IP>:30007
```

The Flask GUI dashboard should appear.

---

9. Kubernetes Verification Commands

 View Pods

```bash
kubectl get pods
```

 View Logs

```bash
kubectl logs <pod-name>
```

Scale Application

```bash
kubectl scale deployment climate-farm-deployment --replicas=3
```

### Self-Healing Test

```bash
kubectl delete pod <pod-name>
```

Kubernetes automatically recreates the pod.

---

 10. Exam Explanation (Short Version)

"The Flask-based AI application was containerized using Docker, pushed to a container registry, and deployed on Kubernetes using Deployment and Service YAML files. Kubernetes provides scalability, self-healing, and exposes the application through a NodePort service."

---

 End of Document
