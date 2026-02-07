from screens.menu import constants
def help_screen(root):
    root.show_message_popup(constants.HELP_SCREEN_HEADER_TEXT,constants.HELP_SCREEN_MAIN_TEXT)