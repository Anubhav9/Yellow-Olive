CHALLENGE_17_TEXT = """The claim inspector can read public notices now.
That part of the ledger looks clean.

But PsyQuack keeps staring at the Vault page.

The Mayor checks another licence.

"This one is for Vault audits."
"Only my audit identity should hold it."

Team Evil changed the holder.
The claim inspector can still reach the Vault.

Fix the Vault access licence so the Mayor's audit identity holds it instead.

Objective:
RoleBinding: vault-access
Namespace: gold-rush-city
Allowed ServiceAccount: mayor-audit-sa
Claim inspector must not access the Vault Secret.
Vault Secret: city-vault-gold

File: rolebinding-q17.yaml
"""
