minikube start
while [ "$(minikube status --format '{{.Host}}')" != "Running" ]; do
  echo "Waiting for minikube..."
  sleep 2
done
kubectl apply -f challenge_files/pod-q1.yaml
