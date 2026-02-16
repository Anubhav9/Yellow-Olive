import asyncio
from textual.widgets import RichLog,Input
from textual import events
from screens import name_input_screen
from screens.name_input_screen import NameInputScreen
from dialouges import author_info


class AuthorInfo(RichLog):
    can_focus = True

    def __init__(self, **kwargs):
        # We pass markup=True here so you don't have to remember it later
        super().__init__(markup=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.focus()

    async def details_about_author(self,color):
        all_details=author_info.AUTHOR_INFO
        all_details=all_details.split("\n")
        for i in range(0,len(all_details)):
            line=all_details[i]
            styled_line = f"[bold {color}]{line}[/]"
            self.write(styled_line+"\n")
            await asyncio.sleep(1.5)

