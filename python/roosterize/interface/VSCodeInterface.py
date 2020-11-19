from pygls.features import WINDOW_SHOW_MESSAGE_REQUEST
from pygls.server import LanguageServer
from pygls.types import MessageActionItem, MessageType, ShowMessageRequestParams

from roosterize.interface.CommandLineInterface import CommandLineInterface


class VSCodeInterface(CommandLineInterface):

    def __init__(self):
        super().__init__()
        self.ls: LanguageServer = None

    def set_language_server(self, ls: LanguageServer):
        self.ls = ls

    def ask_for_confirmation(self, text: str) -> bool:
        yes = MessageActionItem("yes")
        no = MessageActionItem("no")
        future = self.ls.lsp.send_request(
            WINDOW_SHOW_MESSAGE_REQUEST,
            params=ShowMessageRequestParams(MessageType.Warning, text, [yes, no]),
        )

        selected = future.result()
        if selected.title == "yes":
            return True
        else:
            return False

    def show_message(self, text: str):
        self.ls.show_message(text)
