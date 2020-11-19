from pygls.server import LanguageServer

from roosterize.interface.CommandLineInterface import CommandLineInterface

from roosterize.Utils import Utils


class RoosterizeLanguageServer(LanguageServer):
    CMD_SUGGEST_NAMING = "extension.roosterize.suggest_naming"
    CMD_DOWNLOAD_MODEL = "extension.roosterize.download_model"
    CMD_IMPROVE_MODEL = "extension.roosterize.improve_model"

    CONFIGURATION_SECTION = "RoosterizeServer"

    def __init__(self):
        super().__init__()


roosterize_server = RoosterizeLanguageServer()
ui = CommandLineInterface()


@roosterize_server.command(RoosterizeLanguageServer.CMD_SUGGEST_NAMING)
def suggest_naming(ls, *args):
    ls.show_message(f"From server! suggest_naming args: {args}")


@roosterize_server.command(RoosterizeLanguageServer.CMD_DOWNLOAD_MODEL)
def download_model(ls, *args):
    ls.show_message(f"From server! download_model args: {args}")
    # TODO: allow back-and-forth UI here
    ui.download_global_model(force_yes=True)


@roosterize_server.command(RoosterizeLanguageServer.CMD_IMPROVE_MODEL)
def improve_model(ls, *args):
    ls.show_message(f"From server! improve_model args: {args}")


def start_server(**options):
    tcp = Utils.get_option_as_boolean(options, "tcp", default=True)
    host = options.get("host", "127.0.0.1")
    port = options.get("port", 20145)  # Default port is for debugging

    if tcp:
        roosterize_server.start_tcp(host, port)
    else:
        roosterize_server.start_io()
#
# class VSCodeInterface:
#     """
#     Interfaces to the VSCode plugin.
#     """
#
#     roosterize_server = RoosterizeLanguageServer()
#
#     # The port number used for debugging (when the server is started manually)
#     DEBUG_PORT = 20145
#
#     def __init__(self, **options):
#         # self.proj_mgr = proj_mgr
#         print(options)
#
#     def start(self):
#         server = LanguageServer()
#         server.start_tcp("localhost", self.DEBUG_PORT)
#
#     @self.roosterize_server
#     def download_model(self):
#         model_dir = self.proj_mgr.get_model_dir()
#         IOUtils.mk_dir(model_dir)
#
#         # TODO: Download model from a default URL to model_dir
#         pass
#
#     def suggest_name(self, file: Path):
#         self.require_processed_file(file)
#         pass
#
#     def process_file(self, file: Path):
#         # TODO async
#         pass
#
#     def require_processed_file(self, file: Path):
#         # TODO non async
#         pass
