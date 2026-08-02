"""CLI entry point for hosted lab session bootstrap."""

import argparse
import sys
from pathlib import Path

HOSTED_LABS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = HOSTED_LABS_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hosted_labs.core.session import bootstrap_challenge_session, validate_challenge_session


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap a hosted lab challenge session.")
    parser.add_argument(
        "--challenge",
        default="challenge_1",
        help="Challenge folder name under hosted_labs/challenges/ (default: challenge_1)",
    )
    parser.add_argument(
        "--github-id",
        default="github-12345678",
        help="Formatted GitHub user id used as the session namespace",
    )
    parser.add_argument(
        "--session-id",
        default="yo-sess-a8f31",
        help="Ephemeral session id stamped onto resources",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render manifests without calling kubectl apply",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate challenge resources in the session namespace",
    )
    args = parser.parse_args()

    if args.validate:
        result = validate_challenge_session(
            challenge_slug=args.challenge,
            formatted_github_user_id=args.github_id,
        )
        print(f"Challenge: {result['challenge_slug']}")
        print(f"Namespace: {result['namespace']}")
        print(f"Passed: {result['passed']}")
        print(result["message"])
        for check in result["checks"]:
            status = "ok" if check["passed"] else "fail"
            print(f"- [{status}] {check['kind']}/{check['name']}: {check['message']}")
        raise SystemExit(0 if result["passed"] else 1)

    result = bootstrap_challenge_session(
        challenge_slug=args.challenge,
        formatted_github_user_id=args.github_id,
        session_id=args.session_id,
        apply=not args.dry_run,
    )

    print(f"Challenge: {result['challenge_slug']}")
    print(f"Namespace: {result['formatted_github_user_id']}")
    print(f"Session: {result['session_id']}")
    print()
    print(result["challenge_text"])

    if args.dry_run:
        print("\n--- Rendered manifests (dry run) ---")
        for manifest in result["manifests"]:
            print(f"\n# {manifest['name']}")
            print(manifest["yaml"].rstrip())
        return

    print("\n--- Applied manifests ---")
    for message in result["apply_messages"]:
        print(f"{message['name']}: {message['message']}")


if __name__ == "__main__":
    main()
