# mtg_brawlpioneer
Validation tool for custom format: Brawl Pioneer

## SOLUTION TO KEEP THE PROJECT UPDATED
* Each banlist is stored as `JSON` file of condensed data from official source (in `mtgdc_banlists > banlists` folder).
* Static files are generated after each push.

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

### HOW TO ADD A NEW BANLIST
1. Put the new banlist file into `./banlists` with name `%Y-%m-%d.json`.
1. Commit and push the changes to your repository, it will trigger the generation of new static files.

*It works the same for editing and removing a banlist.*

## REQUIIREMENTS
This project runs using Python (v3.11+).

## INSTALLATION
To install all required packages run:

```bash
python3 -m venv venv
source venv/bin/activate
git clone https://github.com/Spigushe/mtg_brawlpioneer.git
pip install -e .
```
