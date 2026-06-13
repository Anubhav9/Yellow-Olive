import global_constants

LAB_INSPECTION_PAUSE_SECONDS = 5

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
QUIT_AND_COME_BACK_PROMPT = (
    "[yellow]Use Quit from the menu, fix the issues above, and come back when ready.[/]"
)
AUDIO_CHECK_PLAYING_MESSAGE = (
    "[bold]Audio check (optional)[/]\n"
    "Playing a short test sound on this machine's speakers..."
)
AUDIO_CHECK_PLAYED_MESSAGE = (
    "If you heard two beeps, audio is working.\n"
    "If not, check volume and output on your system "
    "(for example: alsamixer, speaker-test, or SDL_AUDIODRIVER=alsa on Linux).\n"
    "[dim]The game will continue either way.[/]"
)
AUDIO_CHECK_UNAVAILABLE_MESSAGE = (
    "[bold]Audio check (optional)[/]\n"
    "[yellow]Audio playback is unavailable on this system. "
    "The game will run, but music may be silent.[/]\n"
    "On Linux, try: alsamixer, speaker-test, or run with SDL_AUDIODRIVER=alsa.\n"
    "[dim]The game will continue either way.[/]"
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
    "This may take a few minutes, especially on first run.[/]"
)
CLUSTER_BOOTSTRAP_STILL_WORKING_MESSAGE = (
    "[yellow]Still preparing the lab cluster... "
    "First run can take several minutes while images download.[/]"
)
