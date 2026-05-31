CHALLENGE_13_TEXT = """NodePort was the town gate.
Now Signal Town needs a proper front door — one hostname,
one path, straight to Bulba Baby.
An Ingress will route outside HTTP traffic to bulba-baby-service.
Team Evil left the gate aimed at the wrong Service and port.
Fix the Ingress so bulba-baby.signal-town.local
reaches bulba-baby-service on port 80.

Hint: enable ingress on Minikube if needed:
minikube addons enable ingress

Objective:
Ingress: signal-town-gate
Namespace: signal-town
Host: bulba-baby.signal-town.local
Backend service: bulba-baby-service
Backend port: 80
"""
