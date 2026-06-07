CHALLENGE_16_TEXT = """The notice-board licence is fixed.
But a licence does nothing until someone holds it.

The Mayor points to one name in the ledger.

"This is the claim inspector."
"They may read public notices."
"Nobody else should get this licence."

Team Evil changed the holder.
The RoleBinding points to the wrong ServiceAccount.

Fix the RoleBinding so claim-inspector-sa receives the claim-notice-reader Role.

Objective:
RoleBinding name: claim-inspector-notice-reader
Namespace: gold-rush-city
ServiceAccount: claim-inspector-sa
Role: claim-notice-reader
Only the claim inspector should receive this licence.

File: rolebinding-q16.yaml
"""
