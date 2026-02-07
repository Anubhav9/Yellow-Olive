import py_cui
from numpy.core.defchararray import lower

from screens.menu import dialouges
from screens.menu.dialouges import PROFESSOR_BALD_DIALOGUE_6


def initial_load_start_game(root):
    game=root.add_text_block("",0,2,24,10)
    game.set_text("")
    return game

def control_flow_game(root,game):
    #Step 1 - Load Professor Bald Uncle
    with open("ascii_arts/ascii_professor_bald_uncle.txt","r") as f:
        art_data=f.read()
    final_text=""
    for i in range(0,5):
        dialogue_number=f"PROFESSOR_BALD_DIALOGUE_{i+1}"
        text=getattr(dialouges,dialogue_number)
        text=text+"\n"
        final_text=final_text+text
    final_text=final_text+"\n"+art_data
    game.set_text(final_text)
    root.move_focus(game)

    def ask_name():
        root.show_text_box_popup("What's your name, young talent ? ",get_name_callback)

    def get_name_callback(user_name):
        # Clear the current screen or transition to the next part of the game
        text=dialouges.PROFESSOR_BALD_DIALOGUE_6.replace("{user_name}",user_name)+"\n"+dialouges.PROFESSOR_BALD_DIALOGUE_7
        game.set_text(text)
        root.move_focus(game)
        game.add_key_command(py_cui.keys.KEY_ENTER,ask_user_confirmation)

    def get_user_confirmation(confirmation_text):
        confirmation_text=lower(confirmation_text)
        final_text=""
        if confirmation_text=="yes":
            for i in range(8,14):
                text=getattr(dialouges,f"PROFESSOR_BALD_DIALOGUE_{i}")
                text=text+"\n"
                final_text=final_text+text
        with open("ascii_arts/ascii_art_electromon.txt","r") as f:
            art_data=f.read()
        final_text=final_text+"\n"+art_data
        game.set_text(final_text)

    def ask_user_confirmation():
        root.show_text_box_popup("Are you ready to start your journey now ?",get_user_confirmation)
    game.add_key_command(py_cui.keys.KEY_ENTER, ask_name)



