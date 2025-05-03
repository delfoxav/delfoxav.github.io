---
layout: post
title: Create a self-hosted-kubernetes-server-with-k3s
date: 2025-05-03 13:36 +0200
categories: [Projects, Homemade ML]
tags: [Containers, Kubernetes, data science, machine learning, self-hosted]

---

{% assign image_path = "/assets/images/projects/homemade_ml/self_hosted_clearml/" %}

# Create a self hosted Kubernetes server with k3s

## Table of contents
- [Create a self hosted Kubernetes server with k3s](#create-a-self-hosted-kubernetes-server-with-k3s)
  - [Table of contents](#table-of-contents)
  - [Background](#background)
  - [Installing k3s](#installing-k3s)
  - [installing the dashboard](#installing-the-dashboard)
  - [Create a service account and a cluster role binding](#create-a-service-account-and-a-cluster-role-binding)
  - [Setting up an ingress controller](#setting-up-an-ingress-controller)
  - [add clearml to the helm chart](#add-clearml-to-the-helm-chart)

## Background

Continuing my series of self-hosted projects, I wanted to set up a Kubernetes server on my home lab. Kubernetes is a powerful container orchestration platform that allows you to manage and deploy containerized applications at scale. It is widely used in the industry and is a great tool for managing machine learning workloads. In this post, I will walk you through the process of setting up a self-hosted Kubernetes server using k3s, a lightweight version of Kubernetes that is easy to install and manage.

## Installing k3s
The installation of k3s is very simple. You can install it using the following command:

```bash
curl -sfL https://get.k3s.io | sh -
```

That should be enough to install k3s on our server. We can check if we have a node running by using the following command:

```bash
sudo k3s kubectl get nodes
```

<div style="text-align: center;">
    <img src="{{ image_path }}running_node.png" alt="running_Kubernetes_node" width="600px">
    <p><em>Figure 1: My initial kubernetes node running</em></p>
</div>

## installing the dashboard

Well that's nice, we have a node running. However, I would also like to have a dashboard to manage my Kubernetes cluster. For that, we can use kubernetes-dashboard. For installing this one and most of the other applications, we will use [helm](https://helm.sh/docs/intro/install/). Helm is a package manager for Kubernetes that allows you to easily install and manage applications on your cluster. There's multiple ways to install helm, but as I like apt as a package manager, I will use the following command:

```bash
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

To let helm have access to our Kubernetes cluster, we need to set up the kubeconfig file. This file is used by kubectl to access the Kubernetes API server. By default, k3s stores the kubeconfig file in `/etc/rancher/k3s/k3s.yaml`. We can copy this file to our home directory and set the `KUBECONFIG` environment variable to point to it:

```bash
mkdir -p $HOME/.kube
sudo cp /etc/rancher/k3s/k3s.yaml $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
export KUBECONFIG=$HOME/.kube/config
```

Let's also mmake this export permanent by adding it to our `.bashrc` file:

```bash
echo "export KUBECONFIG=$HOME/.kube/config" >> ~/.bashrc
source ~/.bashrc
```


Now we can install [Kubernetes's dashboard](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/):

```bash
# Add kubernetes-dashboard repository
helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/
# Deploy a Helm Release named "kubernetes-dashboard" using the kubernetes-dashboard chart
helm upgrade --install kubernetes-dashboard kubernetes-dashboard/kubernetes-dashboard --create-namespace --namespace kubernetes-dashboard
```

That should be it. Now let's forward the dashboard to our localhost:

```bash
kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard -n kubernetes-dashboard 8080:443
```
<div style="text-align: center;">
    <img src="{{ image_path }}kubernetes_dashboard.png" alt="kubernetes_dashboard" width="600px">
    <p><em>Figure 2: The kubernetes dashboard</em></p>
</div>

Mmmhh it seems like it's asking for a token to access the dashboard. We can get this token by creating a service account and a cluster role binding. 

## Create a service account and a cluster role binding

First we create a readonly service account:

```bash
kubectl create serviceaccount readonly-user -n kubernetes-dashboard
```

Then we create a cluster role binding that will bind 'readonly-user' to the 'view' cluster role. The view cluster role allows read-only access to the cluster. This means that the readonly-user will be able to see all the resources in the cluster, but will not be able to modify them.

```bash
kubectl create clusterrolebinding readonly-user-view \
  --clusterrole=view \
  --serviceaccount=kubernetes-dashboard:readonly-user
```

To see everything that is going on our cluster, we will also need some access to the RBAC Resources, Storage Resources, Secrets Resources,
Nodes Resource, PersistentVolumes Resource, ClusterRoleBindings Resource, CustomResourceDefinitions Resource.

We can do this by creating a custom cluster role that will give us access to all the resources we need. We can do this by creating a file called `readonly-cluster_role_full.yaml` with the following content:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: readonly-rbac-role
rules:
  # RBAC Resources
  - apiGroups: ["rbac.authorization.k8s.io"]
    resources: ["clusterrolebindings", "clusterroles", "rolebindings", "roles"]
    verbs: ["get", "list"]

  # Storage Resources
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list"]

  # Secrets Resources
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get", "list"]

  # Nodes Resources
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list"]

  # PersistentVolumes Resources
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list"]

  # CustomResourceDefinitions Resources
  - apiGroups: ["apiextensions.k8s.io"]
    resources: ["customresourcedefinitions"]
    verbs: ["get", "list"]

  # Ingress Classes Resources
  - apiGroups: ["networking.k8s.io"]
    resources: ["ingressclasses"]
    verbs: ["get", "list"]

```

Now we can apply this file to our cluster:

```bash
kubectl apply -f readonly-cluster_role_full.yaml
```

Next we have to bind this cluster role to our readonly-user service account. We can do this by creating a file called `readonly-cluster_role_binding.yaml` with the following content:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: readonly-user-binding  # Name of the binding
subjects:
- kind: ServiceAccount
  name: readonly-user
  namespace: kubernetes-dashboard
roleRef:
  kind: ClusterRole
  name: readonly-rbac-role  # Name of the ClusterRole
  apiGroup: rbac.authorization.k8s.io
```

Now we can apply this file to our cluster:

```bash
kubectl apply -f readonly-cluster_role_binding.yaml
```


And finally we can get the token for the readonly-user service account:

```bash
kubectl -n kubernetes-dashboard create token readonly-user
```

<div style="text-align: center;">
    <img src="{{ image_path }}kubernetes_dashboard_token.png" alt="kubernetes_dashboard_token" width="600px">
    <p><em>Figure 3: The kubernetes dashboard token</em></p>
</div>

It looks great! But I am not a fan of having to forward the dashboard to my localhost every time I want to access it. So let's set up an ingress controller to access the dashboard from the outside world (but still within my home network as I haven't exposed it to the internet). 

## Setting up an ingress controller

For that, we will use [nginx-ingress](https://kubernetes.github.io/ingress-nginx/deploy/) as our ingress controller. We can install it using the following command:

```bash
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

Next we need to create an ingress resource that will route traffic to the kubernetes-dashboard service. We can do this by creating a file called `kubernetes-dashboard-ingress.yaml` with the following content:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kubernetes-dashboard
  namespace: kubernetes-dashboard
  annotations:
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - mldataserver
      secretName: mldataserver-tls  # Must match the name of your TLS secret
  rules:
    - host: mldataserver
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: kubernetes-dashboard-web
                port:
                  number: 8000

```

As you might have noticed, this config expects a TLS certificate to be present in the `kubernetes-dashboard-tls` secret. We can create a self-signed certificate for this domain using the following command:

```bash
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout dashboard.key \
  -out dashboard.crt \
  -subj "/CN=mldataserver.kubernetesdashboard" \
  -addext "subjectAltName=DNS:mldataserver.kubernetesdashboard"
```

Then we can create a secret from this certificate:

```bash
kubectl create secret tls kubernetes-dashboard-tls \
  --namespace kubernetes-dashboard \
  --cert=dashboard.crt \
  --key=dashboard.key

```

and finally we can apply the ingress resource to our cluster:

```bash
kubectl apply -f kubernetes-dashboard-ingress.yaml
```

Unfortunately as I don't have a dns setup yet, I will have to follow the port forward by this nignx ingress controller. We can gather the port by running the following command:

```bash 
kubectl get svc -n ingress-nginx
```

in ports you should see a port that looks like `80:31682/TCP,443:31874/TCP`. Giving you the port to access the dashboard using http or https.


## add clearml to the helm chart

Now that we have a kubernetes cluster running, we can add clearml to it. We can do this by using the following command:

```bash
helm repo add clearml https://clearml.github.io/clearml-server
helm repo update
```

We need to link it to our current clearml server. To do so we need some credentials. We can get them from the clearml UI. Go to Settings > Workspace and click Create New Credentials. A popup will appear with the credentials.

<div style="text-align: center;">
    <img src="{{ image_path }}clearml_credentials.png" alt="Getting_your_clearml_credentials" width="600px">
    <p><em>Figure 4: The clearml credentials button</em></p>
</div>

Then we can create a file called `values.yaml` with the following content:


```yaml


Then we can install clearml using the following command:  
```
helm install clearml clearml/clearml
```
