# mtg_brawlpioneer
Diverse tools for custom format: Brawl Pioneer:
- [X] [Decklist Validator](https://spigushe.github.io/mtg_brawlpioneer/decklist_validator.html)
- [X] [Annnouncement history](https://spigushe.github.io/mtg_brawlpioneer/announcement_history.html)
- [X] [JSON banlist](https://spigushe.github.io/mtg_brawlpioneer/current_banlist.json)
- [ ] Rules
- [ ] Committee Presentation

## KEEPING THE PROJECT UP-TO-DATE
* Each banlist is stored as `JSON` file of condensed data from official source (in `mtgdc_banlists > banlists` folder).
* Static files listed above are generated after each push.

### HOW TO ADD A NEW BANLIST
1. Put the new banlist file into `./mtgbp_banlists/banlists` with name `%Y-%m-%d.json`.
1. Commit and push the changes to your repository, it will trigger the generation of new static files.

*It works the same for editing and removing a banlist.*

### BANLIST FILE FORMATTING
File name must be `%Y-%m-%d.json` format with the following template:
```json
[
    {
        "date": "2020-11-20",
        "link": "",
        "special": "",
        "newly_banned_as_commander": [],
        "newly_unbanned_as_commander": [],
        "newly_banned_in_deck": [],
        "newly_unbanned_in_deck": [],
        "explanations": {}
    }
]
```


## REQUIREMENTS
This project runs using Python (v3.11+).

## INSTALLATION
To install all required packages run:

```bash
python3 -m venv venv
source venv/bin/activate
git clone https://github.com/Spigushe/mtg_brawlpioneer.git
pip install -e .
```
