import requests
import json

banlist_data = {}
GOATAPI = "https://ygoprodeck.com/api/banlist/getBanList.php?list=Goat&date=2005-08-17"
EDISONAPI = "https://ygoprodeck.com/api/banlist/getBanList.php?list=Edison&date=2010-03-01"

def format_name(name):
    if name.lower() == "forbidden" or name.lower() == "banned":
        return "Banned"
    return name

def create_banlist_file(name, cards):
    for card in cards:
        banlist_data[card['id']] = format_name(card['status_text'])

    with open(name, 'w', encoding='utf-8') as f:
        json.dump(banlist_data, f, indent=2, ensure_ascii=False)


data = requests.get(GOATAPI).json()
create_banlist_file("goat.json", data)

data = requests.get(EDISONAPI).json()
create_banlist_file("edison.json", data)


