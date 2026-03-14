CHALLENGE_ID=$1
kubectl delete pods --all
POD_FILE="challenge_files/pod-q${CHALLENGE_ID}.yaml"

if [ ! -f "${POD_FILE}" ]; then
  echo "Challenge pod file not found: ${POD_FILE}"
  exit 1
fi

kubectl apply -f "${POD_FILE}"
