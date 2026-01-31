# Deploying to Azure Kubernetes Service (AKS)

This guide describes how to deploy your Flask microservice to Azure Kubernetes Service (AKS) with automated CI/CD using GitHub Actions.

## Prerequisites

1.  **Azure Account**: [Sign up for free](https://azure.microsoft.com/free/).
2.  **Azure CLI**: [Install the Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).
3.  **GitHub Repository**: You need admin access to this repository.
4.  **kubectl**: [Install kubectl](https://kubernetes.io/docs/tasks/tools/).

## Step 1: Login to Azure

Open your terminal and log in to Azure:

```bash
az login
```

## Step 2: Create Resource Group

```bash
# Replace variables as needed
RG_NAME=flask-aks-rg
LOCATION=eastus

az group create --name testresource --location $LOCATION
```

## Step 3: Create Azure Container Registry (ACR)

```bash
ACR_NAME=myflaskacr$RANDOM  # Must be globally unique

az acr create --resource-group testresource --name flasktestreg --sku Basic
```

## Step 4: Create AKS Cluster

Create an AKS cluster and attach it to the ACR so it can pull images.

```bash
CLUSTER_NAME=flask-aks-cluster

az aks create \
    --resource-group testresource \
    --name flasktestreg \
    --node-count 1 \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --attach-acr flasktestreg
```

## Step 5: Get AKS Credentials

Configure `kubectl` to connect to your new cluster.

```bash
az aks get-credentials --resource-group testresource --name flasktestreg
```

Verify connection:

```bash
kubectl get nodes
```

## Step 6: Create Service Principal for GitHub Actions

Create a service principal that has permission to push to ACR and deploy to AKS.

```bash
SUBSCRIPTION_ID=$(az account show --query id --output tsv)

az ad sp create-for-rbac \
  --name "gh-action-aks" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/testresource \
  --sdk-auth
```

Copy the JSON output. This is your `AZURE_CREDENTIALS`.

## Step 7: Configure GitHub Secrets

Go to your repository **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**.

Add the following secrets:

| Secret Name | Value |
| :--- | :--- |
| `AZURE_CREDENTIALS` | The JSON output from Step 6. |
| `ACR_NAME` | The name of your ACR (e.g., `myflaskacr12345`). |
| `CLUSTER_NAME` | The name of your AKS cluster (e.g., `flask-aks-cluster`). |
| `RESOURCE_GROUP` | The name of your resource group (e.g., `flask-aks-rg`). |

## Step 8: Update Manifests (One-time setup)

Open `k8s/deployment.yaml` in your repository and verify the image name matches your ACR. The workflow will attempt to update this, but it's good practice to ensure it's correct or templated.
(The provided workflow handles image replacement automatically).

## Step 9: Trigger Deployment

1.  Push your changes to `main`.
2.  Watch the Action in the **Actions** tab.

## Verification

Once the action completes, get the external IP of your service:

```bash
kubectl get service flask-service
```

Visit `http://<EXTERNAL-IP>` in your browser.
