import global_constants

CONSENT_BODY = (
    "[bold]Optional diagnostics[/]\n"
    "Help improve Yellow Olive with anonymous gameplay and error reports.\n"
    "No cluster data, secrets, or personal info."
)
CONSENT_PROMPT = (
    f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
    "Type `yes` to opt in, or `no` to skip.[/]"
)
INVALID_ANSWER_HINT = (
    "[yellow]Try `yes` (opt in) or `no` (skip).[/]"
)
