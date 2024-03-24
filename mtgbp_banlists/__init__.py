""""""

import glob
import json
import os
from pathlib import Path

import pkg_resources


class BanlistCompiler:
    def __init__(self) -> None:
        self._json = {}
        self._dates = []
        self._current = {}

        self._load_banlists()

    def _load_banlists(self) -> None:
        """Private method that loads ban lists from the package data."""
        try:
            banlists_path = pkg_resources.resource_filename(
                "banlist_handler", "banlists"
            )
        except ModuleNotFoundError:
            banlists_path = Path(__file__).parent / "banlists"

        json_files = [file for file in glob.glob(os.path.join(banlists_path, "*.json"))]

        for filepath in json_files:
            with open(filepath, "r", encoding="utf-8") as fp:
                date_annonce = filepath.split("/")[-1][:-5]
                self._dates.append(date_annonce)
                self._json[date_annonce] = json.load(fp)[0]


class JSONBanlist(BanlistCompiler):
    def __init__(self) -> None:
        super().__init__()
        self._walk()

    def _walk(self) -> None:
        """Private method that handles the generation of the banlist dict."""
        cz_bans = set()
        md_bans = set()

        for date in sorted(self._dates):
            cz_bans = cz_bans | set(self._json[date]["newly_banned_as_commander"])
            cz_bans = cz_bans - set(self._json[date]["newly_unbanned_as_commander"])
            md_bans = md_bans | set(self._json[date]["newly_banned_in_deck"])
            md_bans = md_bans - set(self._json[date]["newly_unbanned_in_deck"])

        self._current = {
            "banned_commanders": sorted(list(cz_bans)),
            "banned_cards": sorted(list(md_bans)),
        }

    @staticmethod
    def export(output_filename="") -> None:
        """Procedure that generates the `.json` version of the banlist in the current folder."""
        banlist = JSONBanlist()

        filepath = Path().absolute()
        filename = (output_filename or "current_banlist") + ".json"

        if os.path.exists(filepath / filename):
            (filepath / filename).unlink()

        with open(filepath / filename, "xt", encoding="utf-8") as outf:
            json.dump(
                banlist._current, outf, ensure_ascii=False, indent=4, sort_keys=True
            )
