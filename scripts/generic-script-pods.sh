CHALLENGE_ID=$1
POD_FILE=$2
kubectl delete pods --all

if [ -z "${POD_FILE}" ]; then
  POD_FILE="challenge_files/pod-q${CHALLENGE_ID}.yaml"
fi

if [ ! -f "${POD_FILE}" ]; then
  echo "Challenge pod file not found: ${POD_FILE}"
  exit 1
fi

kubectl apply -f "${POD_FILE}"
