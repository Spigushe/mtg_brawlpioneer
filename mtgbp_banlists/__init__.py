import glob
import html
import json
import os
from datetime import datetime
from pathlib import Path

import pkg_resources


class BanlistCompiler(object):
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

        self._dates = sorted(self._dates, reverse=True)

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

            if not banlists_path.is_dir():
                raise FileNotFoundError(
                    f"Banlist directory '{banlists_path}' not found."
                )

        self._banlists_path = banlists_path

    def _get_static_directory(self) -> None:
        """
        Validates if the static directory exists.

        Raises:
            FileNotFoundError: If the static directory is not found.
        """
        try:
            static_path = pkg_resources.resource_filename("banlist_handler", "static")
        except ModuleNotFoundError:
            static_path = Path(__file__).parent / "static"

            if not static_path.is_dir():
                raise FileNotFoundError(f"Banlist directory '{static_path}' not found.")

        self._static_path = static_path

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
    def export() -> None:
        """Procedure that generates the '.json' version of the banlist in the current folder.

        This method exports the current state of the banlist to a JSON file.

        Returns:
            None
        """
        banlist = JSONBanlist()

        filepath = Path().absolute() / "docs"
        filename = "current_banlist.json"

        # If the file already exists, delete it
        if os.path.exists(filepath / filename):
            (filepath / filename).unlink()

        with open(filepath / filename, "xt", encoding="utf-8") as outf:
            json.dump(
                banlist._current, outf, ensure_ascii=False, indent=4, sort_keys=True
            )


class HTMLBanlist(BanlistCompiler):
    def __init__(self) -> None:
        super().__init__()

        self._get_static_directory()
        self.header = self._get_static_html("header.html")
        self.header += self._get_static_html("header_history.html")
        self.footer = self._get_static_html("footer_history.html")
        self.footer += self._get_static_html("footer.html")

    @staticmethod
    def export() -> None:
        self = HTMLBanlist()
        banlist_cards = self._get_html_cards()

        filepath = Path().absolute() / "docs"
        filename = "announcement_history.html"

        # If the file already exists, delete it
        if os.path.exists(filepath / filename):
            (filepath / filename).unlink()

        with open(filepath / filename, "xt", encoding="utf-8") as outf:
            outf.write(self.header)
            outf.write(banlist_cards)
            outf.write(self.footer)

    def _get_html_cards(self) -> list[str]:
        return "\n".join([str(HTMLCard(self._json[date])) for date in self._dates])

    def _get_static_html(self, target) -> str:
        with open(str(self._static_path / target), "r", encoding="utf-8") as file:
            return file.read()


class HTMLCard:
    def __init__(self, json_data) -> None:
        self.data = json_data

        self.cz_changes = self._get_changes(zone="cz")
        self.md_changes = self._get_changes(zone="md")

    def __str__(self) -> str:
        card = '<div class="timeline">'
        card += self._get_link()
        card += f'  <span class="year">{self._date_to_str(self.data["date"])}</span>'
        card += '   <div class="timeline-content">'
        card += self._add_changes()
        card += "   </div>"
        card += "</div>"

        return card

    def _get_link(self) -> str:
        link = ""

        if "link" in self.data.keys():
            link = f'<a href="{self.data["link"]}" '
            link += 'title="Go to the official announcement">'
            link += '<i class="fa-solid fa-link"></i></a>'

        return f'<span class="timeline-icon">{link}</span>'

    def _date_to_str(self, date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        month_name = date_obj.strftime("%B")
        year = date_obj.strftime("%Y")
        day = date_obj.strftime("%d")
        day_suffix = (
            "th"
            if 11 <= int(day) <= 13
            else {1: "st", 2: "nd", 3: "rd"}.get(int(day) % 10, "th")
        )

        return f"{month_name} {year}, {day}{day_suffix}"

    def _add_tooltip(self, text, tooltip_dict, symbol=""):
        tooltip = ""

        if text in tooltip_dict.keys():
            tooltip = tooltip_dict[text]
            tooltip = html.escape(tooltip)

        symbol = symbol if symbol else ""
        return (
            f'<span class="card-banlist" data-tooltip="{tooltip}">{symbol}{text}</span>'
        )

    def _get_changes(self, zone) -> list[str]:
        choice = "as_commander" if zone == "cz" else "in_deck" if zone == "md" else ""
        precision = " as a commander" if choice == "as_commander" else ""

        bans = [
            (
                self._add_tooltip(
                    card,
                    self.data["explanations"],
                    '<i class="fa-solid fa-ban text-danger text-decoration-none pe-1"></i>',
                )
                + f" is now <strong>banned</strong>{precision}."
                + "<br>"
            )
            for card in sorted(self.data[f"newly_banned_{choice}"])
        ]
        unbans = [
            (
                self._add_tooltip(
                    card,
                    self.data["explanations"],
                    '<i class="fa-solid fa-check text-success text-decoration-none pe-1"></i>',
                )
                + " is now <strong>legal</strong>."
                + "<br>"
            )
            for card in sorted(self.data[f"newly_unbanned_{choice}"])
        ]

        return bans + unbans

    def _add_changes(self) -> str:
        if not self._has_changes():
            return '<h3 class="title">No Changes</h3>'

        tmp = '<h3 class="title">Changes:</h3>'
        if len(self.cz_changes) > 0:
            tmp += self._display_changes(self.cz_changes)
        if len(self.md_changes) > 0:
            tmp += self._display_changes(self.md_changes)
        if len(self.data["special"]) > 0:
            padding = (
                "other-changes" if len(self.cz_changes + self.md_changes) > 0 else ""
            )
            tmp = (
                "" if padding == "" else tmp
            )  # Display only "Other Changes" if no other changes
            tmp += f'<h3 class="title {padding}">Other Changes:</h3>'
            tmp += f'<p class="description">{self.data["special"]}</p>'

        return tmp

    def _display_changes(self, change_list) -> str:
        tmp = '<p class="description" style="cursor: pointer;">'

        for change in change_list:
            tmp += change

        return tmp + "</p>"

    def _has_changes(self) -> bool:
        return not all(
            [
                len(self.cz_changes) == 0,
                len(self.md_changes) == 0,
                len(self.data["special"]) == 0,
            ]
        )


class HTMLValidator:
    def __init__(self) -> None:
        self._get_static_directory()
        self.header = self._get_static_html("header.html")
        self.page = self._get_static_html("page_validator.html")
        self.footer = self._get_static_html("footer.html")

    def _get_static_directory(self) -> None:
        """
        Validates if the static directory exists.

        Raises:
            FileNotFoundError: If the static directory is not found.
        """
        try:
            static_path = pkg_resources.resource_filename("banlist_handler", "static")
        except ModuleNotFoundError:
            static_path = Path(__file__).parent / "static"

            if not static_path.is_dir():
                raise FileNotFoundError(f"Banlist directory '{static_path}' not found.")

        self._static_path = static_path

    def _get_static_html(self, target) -> str:
        with open(str(self._static_path / target), "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def export() -> None:
        self = HTMLValidator()

        filepath = Path().absolute() / "docs"
        filename = "decklist_validator.html"

        # If the file already exists, delete it
        if os.path.exists(filepath / filename):
            (filepath / filename).unlink()

        with open(filepath / filename, "xt", encoding="utf-8") as outf:
            outf.write(self.header)
            outf.write(self.page)
            outf.write(self.footer)
