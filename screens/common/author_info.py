import asyncio
from textual.widgets import RichLog
from screens.dialouges import author_info


class AuthorInfo(RichLog):
    can_focus = True

    def __init__(self, **kwargs):
        super().__init__(markup=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        """Automatically grab focus when this widget appears."""
        self.focus()

    async def details_about_author(self,color):
        all_details= author_info.AUTHOR_INFO
        all_details=all_details.split("\n")
        for i in range(0,len(all_details)):
            line=all_details[i]
            if not line.strip():
                self.write("")
                await asyncio.sleep(0.3)
                continue
            self.write(line + "\n")
            await asyncio.sleep(0.9)

