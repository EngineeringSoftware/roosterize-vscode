import tempfile
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple

from seutil import BashUtils, IOUtils

from roosterize.data.CoqDocument import CoqDocument
from roosterize.data.DataMiner import DataMiner
from roosterize.data.Definition import Definition
from roosterize.data.Lemma import Lemma
from roosterize.data.ModelSpec import ModelSpec
from roosterize.ml.MLModels import MLModels
from roosterize.ml.naming.NamingModelBase import NamingModelBase
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

    DEFAULT_BEAM_SEARCH_SIZE = 5
    DEFAULT_K = 5

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
        data = self.parse_file(file_path, serapi_options)

        # Load model
        self.load_local_model(prj_root)
        model = self.get_model()

        # Use the model to make predictions
        # Temp dirs for processed data and results
        temp_data_dir = Path(tempfile.mktemp(prefix="roosterize", dir=True))
        temp_data_dir.mkdir(parents=True)

        # Dump lemmas & definitions
        temp_raw_data_dir = temp_data_dir / "raw"
        temp_raw_data_dir.mkdir()
        IOUtils.dump(
            temp_raw_data_dir / "lemmas.json",
            IOUtils.jsonfy(data.lemmas),
            IOUtils.Format.json,
        )
        IOUtils.dump(
            temp_raw_data_dir / "definitions.json",
            IOUtils.jsonfy(data.definitions),
            IOUtils.Format.json,
        )

        # Model-specific process
        temp_processed_data_dir = temp_data_dir / "processed"
        temp_processed_data_dir.mkdir()
        model.process_data_impl(temp_raw_data_dir, temp_processed_data_dir)

        # Invoke eval
        candidates_logprobs = model.eval_impl(
            temp_processed_data_dir,
            beam_search_size=self.DEFAULT_BEAM_SEARCH_SIZE,
            k=self.DEFAULT_K,
        )

        # Save predictions
        IOUtils.rm_dir(temp_data_dir)

        # Report predictions
        self.report_predictions(data, candidates_logprobs)
        return

    def report_predictions(self, data: ProcessedFile, candidates_logprobs: List[List[Tuple[str, float]]]):
        # TODO implement
        print(candidates_logprobs)
        pass

    def load_local_model(self, prj_root: Path) -> None:
        """
        Try to load the local model, if it exists; otherwise do nothing.
        """
        if self.model is None:
            local_model_dir = RoosterizeDirUtils.get_local_model_dir(prj_root)
            if local_model_dir.is_dir():
                model_spec = IOUtils.dejsonfy(
                    IOUtils.load(local_model_dir / "spec.json", IOUtils.Format.json),
                    ModelSpec,
                )
                self.model = MLModels.get_model(model_spec, is_eval=True)

    def get_model(self) -> NamingModelBase:
        """
        Try to get the currently loaded model; if no model is loaded, gets the global model.
        The local model can be loaded by invoking load_local_model (before invoking this method).
        """
        if self.model is None:
            # Load global model
            global_model_dir = RoosterizeDirUtils.get_global_model_dir()
            model_spec = IOUtils.dejsonfy(
                IOUtils.load(global_model_dir / "spec.json", IOUtils.Format.json),
                ModelSpec,
            )
            self.model = MLModels.get_model(model_spec, is_eval=True)
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
