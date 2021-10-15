from git import Repo

from openpecha.cli import download_pecha
from openpecha.config import PECHA_PREFIX
from openpecha.github_utils import commit, create_orphan_branch

from .exporter.bitext import BitextExporter
from .exporter.po import PoExporter
from .segmenters import Segmenter


class Alignment:
    def __init__(self, id=None, segmenter: Segmenter = None):
        self.id = id
        self.segmenter = segmenter
        self.alignment_repo_path = download_pecha(self.id) if self.id else None

    @property
    def alignment_path(self):
        return self.alignment_repo_path / f"{self.id}.opa" / "Alignment.yml"

    def create(self):
        pass

    def create_po_view(self):
        exporter = PoExporter(self.alignment_path)
        repo = Repo(self.alignment_repo_path)
        if not self.is_po_created(repo):
            create_orphan_branch(
                self.alignment_repo_path, "po", parent_branch="main", type_="opa"
            )
        else:
            repo.git.checkout("po")
        exporter.export(self.alignment_repo_path)
        commit(self.alignment_repo_path, "po file added", not_includes=[], branch="po")
        return self.alignment_repo_path

    def is_po_created(self, repo):
        if "po" in repo.branches:
            return True
        else:
            return False

    def get_po_view(self):
        po_views = {}
        exporter = PoExporter(self.alignment_path)
        repo = Repo(self.alignment_repo_path)
        seg_srcs = exporter.alignment.get("segment_sources", {})
        if seg_srcs:
            if not self.is_po_created(repo):
                self.create_po_view()
            else:
                repo.git.checkout("po")
            for pecha_id, pecha_info in seg_srcs.items():
                pecha_type = pecha_info.get("type", "")
                pecha_lang = pecha_info.get("lang", "")
                if pecha_type:
                    po_views[pecha_type] = {
                        "path": self.alignment_repo_path / f"{pecha_lang}.po",
                        "lang": pecha_lang,
                    }
        return po_views

    def create_bitext_view(self):
        exporter = BitextExporter(self.alignment_path)
        create_orphan_branch(
            self.alignment_repo_path, "bitext", parent_branch="main", type_="opa"
        )
        exporter.export(self.alignment_repo_path)
        commit(
            self.alignment_repo_path,
            "bitext file added",
            not_includes=[],
            branch="bitext",
        )
        return self.alignment_repo_path
