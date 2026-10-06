import json
import os
import requests

PACKS_TO_FETCH = [
    {"name": "Legend of Blue Eyes White Dragon", "price": 150, "code": "LOB"},
    {"name": "Metal Raiders", "price": 150, "code": "MRD"},
    {"name": "Magic Ruler", "price": 150, "code": "MRL"},
    {"name": "Pharaoh's Servant", "price": 150, "code": "PSV"},
    {"name": "Labyrinth of Nightmare", "price": 200, "code": "LON"},
    {"name": "Legacy of Darkness", "price": 200, "code": "LOD"},
    {"name": "Pharaonic Guardian", "price": 200, "code": "PGD"},
    {"name": "Magician's Force", "price": 250, "code": "MFC"},
    {"name": "Dark Crisis", "price": 250, "code": "DCR"},
    {"name": "Invasion of Chaos", "price": 300, "code": "IOC"},
]

API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
OUTPUT_RULES = "rules.json"
PACKS_DIR = "packs"

PULL_RATES = {
    "guaranteed_slot": {
        "rare": 75.0,
        "super_rare": 15.0,
        "ultra_rare": 8.0,
        "secret_rare": 2.0
    }
}


def normalize_rarity(rarity_str):
    r = rarity_str.lower()
    if "secret rare" in r:
        return "secret_rare"
    elif "ultra rare" in r:
        return "ultra_rare"
    elif "super rare" in r:
        return "super_rare"
    elif "common" in r or "short print" in r or "normal" in r:
        return "common"
    elif "rare" in r:
        return "rare"
    return "common"


def generate_packs():
    if not os.path.exists(PACKS_DIR):
        os.makedirs(PACKS_DIR)

    headers = {'User-Agent': 'Mozilla/5.0'}
    available_packs = []

    for pack in PACKS_TO_FETCH:
        set_name = pack["name"]
        pack_code = pack["code"]
        price = pack["price"]

        print(f"Obteniendo datos de: {pack_code}...")

        try:
            # Pedimos a la API todas las cartas que pertenezcan a este set
            response = requests.get(API_URL, params={'cardset': set_name}, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code} en {pack_code}. Ignorando.")
                continue

            cards = response.json().get("data", [])

            pools = {"common": set(), "rare": set(), "super_rare": set(), "ultra_rare": set(), "secret_rare": set()}

            for card in cards:
                card_id = card["id"]

                # Buscar la rareza usando el prefijo del código (ej. LOB) en lugar del nombre completo
                added = False
                for s in card.get("card_sets", []):
                    set_code_api = s.get("set_code", "").upper()
                    # Si el código de la carta empieza con "LOB-" o "LOB-EN", la asignamos
                    if set_code_api.startswith(f"{pack_code}-") or set_code_api.startswith(pack_code):
                        rarity_key = normalize_rarity(s["set_rarity"])
                        pools[rarity_key].add(card_id)
                        added = True
                        break  # Ya encontramos la versión de este pack

                # Si por alguna razón la API no detalla el código, la mandamos a common como resguardo
                if not added:
                    pools["common"].add(card_id)

            json_pools = {rarity: sorted(list(id_set)) for rarity, id_set in pools.items()}

            pack_data = {
                "id": pack_code,
                "name": set_name,
                "price": price,
                "image": f"https://images.ygoprodeck.com/images/sets/{pack_code}.jpg",
                "pool": json_pools
            }

            # Guardar el JSON individual del sobre
            pack_filename = os.path.join(PACKS_DIR, f"{pack_code}.json")
            with open(pack_filename, 'w', encoding='utf-8') as f:
                json.dump(pack_data, f, indent=2, ensure_ascii=False)

            available_packs.append(pack_code)
            total = sum(len(lst) for lst in json_pools.values())
            print(f"  ✅ {pack_code}.json creado con {total} cartas.")

        except Exception as e:
            print(f"❌ Error procesando {pack_code}: {e}")

    # Generar el rules.json principal que actúa como índice
    rules_index = {
        "pull_rates": PULL_RATES,
        "available_packs": available_packs
    }

    with open(OUTPUT_RULES, 'w', encoding='utf-8') as f:
        json.dump(rules_index, f, indent=2, ensure_ascii=False)

    print("\n🎉 Proceso completado. Revisa la carpeta /packs/ y rules.json.")


if __name__ == "__main__":
    generate_packs()