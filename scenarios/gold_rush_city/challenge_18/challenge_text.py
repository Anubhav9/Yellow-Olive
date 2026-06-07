CHALLENGE_18_TEXT = """The Vault access in Gold Rush City is fixed.
But the Mayor finds one last permit under the ledger.

This one is different.
It is not stamped for one town.
It is stamped for the whole territory.

Team Evil made a ClusterRole too powerful.
The claim inspector should read public claim notices across towns.
Instead, the permit points at Vault records.

Fix the territory-wide permit so it is safe.

Objective:
ClusterRole: territory-claim-notice-reader
ClusterRoleBinding: territory-claim-notice-access
ServiceAccount: claim-inspector-sa
Allowed resource: public claim notices
Vault access: not allowed anywhere

File: clusterrole-q18.yaml
"""
