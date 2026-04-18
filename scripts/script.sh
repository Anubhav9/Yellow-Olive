if which minikube &> /dev/null
then
    echo "Minikube is installed at $(which minikube)"
else
    echo "Minikube not found."
    exit 1
fi

PROFILE="project-yellow-olive"

minikube start --nodes 1 -p $PROFILE

while [ "$(minikube status -p $PROFILE --format '{{.Host}}')" != "Running" ]; do
  echo "Waiting for minikube..."
  sleep 2
done

kubectl config use-context $PROFILE
