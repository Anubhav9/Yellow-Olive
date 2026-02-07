import py_cui
from screens.menu import constants
import global_constants
from screens.menu import help_screen,start_game

def menu_controller(root,game):
    menu = root.add_scroll_menu("Menu", 0, 0, global_constants.ROW_SPAN, constants.COLUMN_SPAN)
    menu.add_item_list([constants.START_GAME, constants.HELP])
    menu.set_selected_color(py_cui.GREEN_ON_BLACK)
    def on_enter():
        selected_index=menu._selected_item
        if(selected_index==0):
            selected_text=constants.START_GAME
        elif(selected_index==1):
            selected_text=constants.HELP

        if selected_text==constants.HELP:
            help_screen.help_screen(root)
        if selected_text==constants.START_GAME:
            start_game.control_flow_game(root,game)


    menu.add_key_command(py_cui.keys.KEY_ENTER,on_enter)
    return menu


