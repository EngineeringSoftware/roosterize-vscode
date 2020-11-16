from pathlib import Path

from roosterize.ProjectManager import ProjectManager

from seutil import IOUtils


class VSCodeInterface:
    """
    Interfaces to the VSCode plugin.
    """

    def __init__(self, proj_mgr: ProjectManager):
        self.proj_mgr = proj_mgr

    def download_model(self):
        model_dir = self.proj_mgr.get_model_dir()
        IOUtils.mk_dir(model_dir)

        # TODO: Download model from a default URL to model_dir
        pass

    def suggest_name(self, file: Path):
        # TODO
        pass

    def process_file(self, file: Path):
        # TODO
        pass
