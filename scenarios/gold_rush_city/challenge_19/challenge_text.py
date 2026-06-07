CHALLENGE_19_TEXT = """The Mayor finds the name from the torn licence.

team-evil-prospector-sa.

The forged identity Team Evil used to reach the Vault.

Every other licence in Gold Rush City looks safer now.
But this one binding still opens the theft path.

Cut it.
Prove the forged prospector can no longer reach the Vault.
Prove the town's trusted identities still work.

Objective:
RoleBinding: forged-vault-path
Namespace: gold-rush-city
Forged ServiceAccount: team-evil-prospector-sa
Vault Secret: city-vault-gold
Forged identity must not access the Vault.
Mayor audit access: must still work.
Claim inspector notice access: must still work.

File: rolebinding-q19.yaml
"""
