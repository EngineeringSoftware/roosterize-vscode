from typing import Optional

from roosterize.RoosterizeDirUtils import RoosterizeDirUtils

from seutil import IOUtils


class UserInterface:

    def __init__(self):
        return

    @classmethod
    def parse_yes_no_answer(cls, ans: str) -> Optional[bool]:
        if str.lower(ans) in ["y", "yes"]:
            return True
        elif str.lower(ans) in ["n", "no"]:
            return False
        else:
            return None

    def download_global_model(self, force_yes: bool = False):
        """
        Downloads a global Roosterize model.
        """
        global_model_dir = RoosterizeDirUtils.get_global_model_dir()
        if global_model_dir.exists():
            print(f"A Roosterize model already exists at {global_model_dir}")
            ans = self.parse_yes_no_answer(input(f"Do you want to delete it and download again? [yes/no] > "))
            if force_yes:
                ans = True
            if ans != True:
                print(f"Cancelled")
                return
            IOUtils.rm_dir(global_model_dir)

        # TODO download from Macros.url
