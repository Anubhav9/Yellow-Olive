import global_constants

READY_PROMPT = (
    f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
    "So, young engineer, are you ready to step into Yellow Olive?\n"
    "Type `yes` when you are ready to begin.[/]"
)
CHECKING_REQUIREMENTS_PROMPT = (
    f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
    "Professor Bald is inspecting your lab equipment...[/]"
)
REQUIREMENTS_FAILED_PROMPT = (
    f"[bold {global_constants.GLOBAL_DIALOGUE_COLOR}]"
    "Professor Bald cannot open the lab yet.[/]"
)
TITLE_PROFESSOR_BALD_ADVICE = "Professor Bald's Advice"
ACTION_OPEN_SEPARATE_TERMINAL = (
    "[bold red]Open a separate Command Chamber (terminal tab) to speak to "
    "the cluster using kubectl.[/]"
)
PROCEED_TO_CHALLENGE_1 = (
    "\n[reverse] Press Enter to Continue and Proceed to Challenge 1 [/]"
)
CLUSTER_BOOTSTRAP_MESSAGE = (
    "[yellow]Professor Bald is preparing the lab cluster... "
    "This may take up to 60 seconds.[/]"
)
