#!/bin/bash
echo "**** Begin installing k3s"

# Install k3s with a more recent version
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.1+k3s2 K3S_KUBECONFIG_MODE="644" sh -

echo "**** End installing k3s"

# Configure kubectl for vagrant user
mkdir -p /home/vagrant/.kube
cp /etc/rancher/k3s/k3s.yaml /home/vagrant/.kube/config
chown -R vagrant:vagrant /home/vagrant/.kube
echo 'export KUBECONFIG=/home/vagrant/.kube/config' >> /home/vagrant/.bashrc

# Wait for k3s to be ready
echo "Waiting for k3s to start..."
sleep 10
K3S_STATUS=$(kubectl get node 2>/dev/null | grep Ready || echo "NotReady")
while [[ "$K3S_STATUS" != *"Ready"* ]]; do
  echo "K3s not ready yet, waiting..."
  sleep 5
  K3S_STATUS=$(kubectl get node 2>/dev/null | grep Ready || echo "NotReady")
done
echo "K3s is ready!"

# Enable kubectl access from outside the VM
# Uncomment if needed:
# nohup kubectl proxy --address='0.0.0.0' --accept-hosts='.*' &