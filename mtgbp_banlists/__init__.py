import glob
import json
import os
from pathlib import Path

import pkg_resources


class BanlistCompiler:
    """
    Class responsible for loading and managing Brawl Pioneer banlists.
    The banlists are loaded from JSON files stored in the "banlists" directory.
    """

    def __init__(self) -> None:
        """
        Initialize the BanlistCompiler object.
        Loads the banlists from JSON files and sets up internal data structures
        to store and manage them.
        """
        self._dates = []
        self._json = {}

        # Load banlists from the package data or the local directory
        self._get_banlists_directory()
        self._collect_json_files()
        self._parse_json_files()

    def _get_banlists_directory(self) -> None:
        """
        Validates if the banlists directory exists.

        Raises:
            FileNotFoundError: If the banlists directory is not found.
        """
        try:
            banlists_path = pkg_resources.resource_filename(
                "banlist_handler", "banlists"
            )
        except ModuleNotFoundError:
            banlists_path = Path(__file__).parent / "banlists"

            if not self._banlists_path.is_dir():
                raise FileNotFoundError(
                    f"Banlist directory '{banlists_path}' not found."
                )

        self._banlists_path = banlists_path

    def _collect_json_files(self) -> list[str]:
        """
        Collects all JSON files from the banlists directory.

        Returns:
            List[str]: List of JSON file paths.
        """
        json_files = [
            file for file in glob.glob(os.path.join(self._banlists_path, "*.json"))
        ]
        return json_files

    def _parse_json_files(self) -> None:
        """
        Parses the JSON files and populates the _dates and _json attributes.
        """
        json_files = self._collect_json_files()

        for filepath in json_files:
            with open(filepath, "r", encoding="utf-8") as fp:
                date_annonce = filepath.split("/")[-1][:-5]
                self._dates.append(date_annonce)
                self._json[date_annonce] = json.load(fp)[0]


class JSONBanlist(BanlistCompiler):
    def __init__(self) -> None:
        super().__init__()
        self._current = {}

        # Initialize and process the banlist data.
        self._walk()

    def _walk(self) -> None:
        """
        Private method that handles the generation of the banlist dict.

        This method performs set operations on the banned cards to exclude any
        unbanned cards.
        """
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
        """Procedure that generates the '.json' version of the banlist in the current folder.

        This method exports the current state of the banlist to a JSON file.

        Args:
            output_filename (str): Optional argument that specifies the name of the output file.
                                    If no argument is provided, the default filename is 'current_banlist.json'.

        Returns:
            None
        """
        banlist = JSONBanlist()

        filepath = Path().absolute()
        filename = (output_filename or "current_banlist") + ".json"

        # If the file already exists, delete it
        if os.path.exists(filepath / filename):
            (filepath / filename).unlink()

        with open(filepath / filename, "xt", encoding="utf-8") as outf:
            json.dump(
                banlist._current, outf, ensure_ascii=False, indent=4, sort_keys=True
            )
