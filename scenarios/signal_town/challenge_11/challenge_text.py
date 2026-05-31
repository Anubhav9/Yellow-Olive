CHALLENGE_11_TEXT = """Signal Town is alive inside the cluster.
But Professor Bald stands outside the town walls.
He cannot use ClusterIP from out here.
He needs a gate port on every cluster node — a NodePort.
Open bulba-baby-service to the outside world so travellers
can reach Bulba Baby from beyond Signal Town.

Objective:
Service: bulba-baby-service
Namespace: signal-town
type: NodePort
port: 80
targetPort: 80
nodePort: 30080
"""
