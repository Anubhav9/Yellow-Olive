"""Backward-compatible entry point for Challenge 1 validation."""

from hosted_labs.core.validation import validate_challenge_resources

CHALLENGE_SLUG = "challenge_1"


def validate(namespace: str) -> tuple[bool, str]:
    result = validate_challenge_resources(CHALLENGE_SLUG, namespace)
    return result["passed"], result["message"]
