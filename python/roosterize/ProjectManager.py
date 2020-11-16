from typing import Optional
from pathlib import Path

from seutil import IOUtils


class ProjectManager:
    """
    Utility functions to manage .roosterize directory under a project.
    """

    def __init__(self, roosterize_dir: Path):
        self.roosterize_dir = roosterize_dir

    @classmethod
    def auto_infer_roosterize_dir(self, optional_file: Optional[Path] = None) -> Path:
        """
        Automatically infers the appropriate .roosterize directory for the project, which
        should locate in the same directory as _CoqProject does. If a file is provided,
        try to look for the nearest directory that contains the file and has a _CoqProject;
        otherwise, start looking from the current directory instead.

        Returns:
            The inferred .roosterize directory path.
        """
        curp = optional_file
        if curp is None:
            curp = Path.cwd()

        # Find the latest _CoqProject directory
        while True:
            if len(curp) <= 1:
                raise IOError("Cannot find _CoqProject")

            if not curp.is_dir():
                curp = curp.parent
                continue

            if (curp / "_CoqProject").is_file():
                break
            else:
                curp = curp.parent
                continue

        return curp / ".roosterize"

    def get_processed_files_dir(self):
        return self.roosterize_dir / "files"

    def get_model_dir(self):
        return self.roosterize_dir / "models"

    def get_project_dir(self):
        return self.roosterize_dir.parent

    def get_config_path(self):
        return self.roosterize_dir / "config.yml"

    def update_config(self, new_config):
        config = IOUtils.load(self.get_config_path(), IOUtils.Format.yaml)
        config.update(new_config)
        IOUtils.dump(self.get_config_path(), config, IOUtils.Format.yaml)
