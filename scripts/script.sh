# Legacy bootstrap script kept for reference. The game uses start_core_infra_v1()
# in utils/general_utils.py (Python subprocess) instead of invoking this file.
if ! which minikube &> /dev/null; then
    echo "Minikube not found."
    exit 1
fi

PROFILE="project-yellow-olive"
TIMEOUT_SECONDS=60
ELAPSED=0

minikube start --nodes 1 -p "$PROFILE"

cluster_is_ready() {
    minikube status -p "$PROFILE" >/dev/null 2>&1
}

while ! cluster_is_ready; do
    if [ "$ELAPSED" -ge "$TIMEOUT_SECONDS" ]; then
        echo "Cluster failed to become ready within ${TIMEOUT_SECONDS}s."
        exit 1
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

kubectl config use-context "$PROFILE"
