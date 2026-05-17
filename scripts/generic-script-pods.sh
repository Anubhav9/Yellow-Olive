CHALLENGE_ID=$1
POD_FILE=$2
SVC_FILE=$3
EXTRA_POD_FILE=$4

if [ -z "${POD_FILE}" ]; then
  POD_FILE="challenge_files/pod-q${CHALLENGE_ID}.yaml"
fi

if [ ! -f "${POD_FILE}" ]; then
  echo "Challenge pod file not found: ${POD_FILE}"
  exit 1
fi

# Challenge 8+: pod + service in signal-town (optional third arg = svc manifest).
if [ -n "${SVC_FILE}" ] && [ -f "${SVC_FILE}" ]; then
  NAMESPACE_FILE="$(dirname "${POD_FILE}")/namespace-signal-town.yaml"
  if [ -f "${NAMESPACE_FILE}" ]; then
    kubectl apply -f "${NAMESPACE_FILE}"
  fi
  kubectl delete pods --all -n signal-town
  kubectl delete service --all -n signal-town
  if [ -n "${EXTRA_POD_FILE}" ] && [ -f "${EXTRA_POD_FILE}" ]; then
    kubectl apply -f "${EXTRA_POD_FILE}"
    kubectl apply -f "${SVC_FILE}"
    kubectl apply -f "${POD_FILE}"
  else
    kubectl apply -f "${POD_FILE}"
    kubectl apply -f "${SVC_FILE}"
  fi
  exit 0
fi

kubectl delete pods --all
kubectl apply -f "${POD_FILE}"
