import json
import requests
import os
import time

rules_file = json.load(open("rules.json"))
API = "https://db.ygoprodeck.com/api/v7/cardinfo.php?format=goat"
packs_dir = 'packs'
pool = []

# Iterar sobre cada archivo de la carpeta
for filename in os.listdir(packs_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(packs_dir, filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            pack_data = json.load(f)

            # Obtener el pool de este sobre
            pack_pool = pack_data.get('pool', {})
            for key, value in pack_pool.items():
                pool.extend(value)

pool = list(set(pool))
cards = list()
urls = dict()

data = requests.get(API, timeout=60).json()["data"]
for c in data:
    if c['id'] in pool:
        cards.append(
            {
                'id': c.get('id', None),
                'n': c.get('name', None),
                'ty': c.get('type', None),
                'lv': c.get('level', None),
                'a': c.get('atk', None),
                'd': c.get('def', None),
                'ex': "Fusion" in c.get('type', None),
                'img': c["card_images"][0]['id'],
                'desc': c.get('desc', None),
                'r': c.get('race', None),
                'at': c.get('attribute', None)
            }
        )
        urls[c["id"]] = c["card_images"][0]["image_url"]


with open("cards.json", "w", encoding="utf-8") as fh:
    json.dump({"cards": list(cards)}, fh, ensure_ascii=False)

for card in cards:
    path = f"images_hd/{card['img']}.jpg"
    if os.path.exists(path):
        continue
    r = requests.get(urls[card['img']], timeout=30)
    if r.ok:
        open(path, "wb").write(r.content)
    time.sleep(0.1)                                   # límite de la API: 20 req/s
print("listo")
