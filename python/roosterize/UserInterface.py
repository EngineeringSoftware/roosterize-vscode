from pathlib import Path
from typing import List, NamedTuple, Optional

from roosterize.ml.naming.NamingModelBase import NamingModelBase

from roosterize.data.Definition import Definition

from roosterize.data.DataMiner import DataMiner

from roosterize.data.Lemma import Lemma

from roosterize.data.CoqDocument import CoqDocument
from seutil import BashUtils, IOUtils

from roosterize.parser.CoqParser import CoqParser, SexpNode, SexpParser
from roosterize.parser.ParserUtils import ParserUtils
from roosterize.RoosterizeDirUtils import RoosterizeDirUtils


class ProcessedFile(NamedTuple):
    source_code: str
    doc: CoqDocument
    ast_sexp_list: List[SexpNode]
    tok_sexp_list: List[SexpNode]
    unicode_offsets: List[int]
    lemmas: List[Lemma]
    definitions: List[Definition]

class UserInterface:

    def __init__(self):
        self.model: NamingModelBase = None
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

    def infer_serapi_options(self, prj_root: Path) -> str:
        serapi_options = None

        # 1. Try to read from config file
        config_file = RoosterizeDirUtils.get_local_config_file(prj_root)
        if config_file.exists():
            config = IOUtils.load(config_file, IOUtils.Format.json)
            serapi_options = config.get("serapi_options")

        if serapi_options is not None:
            return serapi_options

        # 2. Try to infer from _CoqProject
        coq_project_file = prj_root / "_CoqProject"
        possible_serapi_options = []
        if coq_project_file.exists():
            coq_project = IOUtils.load(coq_project_file, IOUtils.Format.txt)
            for l in coq_project.splitlines():
                if l.strip().startswith("-R "):
                    possible_serapi_options.append(l)

        if len(possible_serapi_options) > 0:
            serapi_options = " ".join(possible_serapi_options)

        if serapi_options is not None:
            return serapi_options

        # Fail to infer serapi options
        raise RuntimeError("Cannot infer SerAPI options. Please specify it in .roosterizerc")

    def suggest_naming(self, file_path: Path, prj_root: Optional[Path] = None):
        """
        Processes a file to get its lemmas and runs the model to get predictions.
        """
        # Infer SerAPI options
        if prj_root is None:
            prj_root = RoosterizeDirUtils.auto_infer_project_root(file_path)

        serapi_options = self.infer_serapi_options(prj_root)

        # Parse file
        processed_file = self.parse_file(file_path, serapi_options)

        # Load model
        self.load_model()

        # TODO use the model to make predictions

    def load_model(self) -> NamingModelBase:
        if self.model is None:
            # TODO load cache model if it exists, otherwise load global model
            pass
        else:
            return self.model

    def parse_file(self, file_path: Path, serapi_options):
        source_code = IOUtils.load(file_path, IOUtils.Format.txt)
        unicode_offsets = ParserUtils.get_unicode_offsets(source_code)
        ast_sexp_str = BashUtils.run(f"sercomp {serapi_options} --mode=sexp -- {file_path}", expected_return_code=0).stdout
        tok_sexp_str = BashUtils.run(f"sertok {serapi_options} --mode=sexp -- {file_path}", expected_return_code=0).stdout

        ast_sexp_list: List[SexpNode] = SexpParser.parse_list(ast_sexp_str)
        tok_sexp_list: List[SexpNode] = SexpParser.parse_list(tok_sexp_str)

        doc = CoqParser.parse_document(
            source_code,
            ast_sexp_list,
            tok_sexp_list,
            unicode_offsets=unicode_offsets,
        )

        # Collect lemmas & definitions
        lemmas: List[Lemma] = DataMiner.collect_lemmas_doc(doc, ast_sexp_list, serapi_options)
        definitions: List[Definition] = DataMiner.collect_definitions_doc(doc, ast_sexp_list)

        return ProcessedFile(source_code, doc, ast_sexp_list, tok_sexp_list, unicode_offsets, lemmas, definitions)
