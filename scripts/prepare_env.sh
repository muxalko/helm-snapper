# install jq
sudo apt -y install jq
# install docker
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo groupadd docker
sudo usermod -aG docker $USER

sudo systemctl enable docker.service
sudo systemctl enable containerd.service

# install kubectl 
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client --output=yaml

# install helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# install k9s
curl -fsSL -o k9s_Linux_x86_64.tar.gz https://github.com/derailed/k9s/releases/download/v0.25.21/k9s_Linux_x86_64.tar.gz
tar zxvf k9s_Linux_x86_64.tar.gz
chmod +x ./k9s
mv k9s /usr/local/bin/
# install kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.14.0/kind-linux-amd64
chmod +x ./kind
mv ./kind /usr/local/bin/kind

# start kind demo cluster
kind create cluster --config kind/demo-cluster.yaml --name demo

# add repo
helm repo add gloo https://storage.googleapis.com/solo-public-helm
helm repo update

# get helm chart
helm pull gloo/gloo

# create sample file
helm template . > ~/workspace/helm-snapper/all-k8s-docs.yaml

# install first (CRDs must be available for helm install --dry-run flag)
kubectl create namespace gloo-system
helm install gloo --debug . -n gloo-system

helm ls -A -o json

#install gloo controller
curl -sL https://run.solo.io/gloo/install | sh
sudo mv .gloo/bin/glooctl /usr/local/bin

# install metalllb
kubectl apply -f scripts/kind/metallb/namespace.yaml
kubectl apply -f scripts/kind/metallb/metallb.yaml

# check networking, use docker network of kind in next step config map
docker network inspect -f '{{.IPAM.Config}}' kind

#update configmap
vi scripts/kind/metallb/metallb-configmap.yaml
#apply configmap
kubectl apply -f scripts/kind/metallb/metallb-configmap.yaml

# TEST
# deploy foo-bar application to check load balancer networking
kubectl apply -f scripts/kind/metallb/foo-bar-app.yaml
LB_IP=$(kubectl get -n gloo-system svc gateway-proxy -o=jsonpath='{.status.loadBalancer.ingress[0].ip}')
# should output foo and bar on separate lines 
for _ in {1..10}; do
  curl ${LB_IP}:5678
done

# configure gloo appv1 route
kubectl apply -f scripts/gloo/echo-http-server-v1.yaml
kubectl apply -f scripts/gloo/echo-http-server-v2.yaml
kubectl apply -f scripts/gloo/upstream.yaml
kubectl apply -f scripts/gloo/virtualservice-subset-v2.yaml
# check gloo subset routing for canary release
# curl http://172.18.0.200/
# version:v1
# url -H 'stage: canary' http://172.18.0.200/
# version:v2 

# using RoutingTable https://itnext.io/two-phased-canary-rollout-with-gloo-part-2-ffa556a503b0

