import json
import os

import requests

API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
OUTPUT_RULES = "rules.json"
PACKS_DIR = "packs"
HEADERS = {"User-Agent": "Mozilla/5.0"}

PACKS_TO_FETCH = [
    {"name": "Legend of Blue Eyes White Dragon", "price": 150, "code": "LOB"},
    {"name": "Metal Raiders", "price": 150, "code": "MRD"},
    {"name": "Magic Ruler", "price": 150, "code": "MRL"},
    {"name": "Pharaoh's Servant", "price": 150, "code": "PSV"},
    {"name": "Labyrinth of Nightmare", "price": 200, "code": "LON"},
    {"name": "Legacy of Darkness", "price": 200, "code": "LOD"},
    {"name": "Pharaonic Guardian", "price": 200, "code": "PGD"},
    {"name": "Magician's Force", "price": 200, "code": "MFC"},
    {"name": "Dark Crisis", "price": 200, "code": "DCR"},
    {"name": "Ancient Sanctuary", "price": 250, "code": "AST"},
    {"name": "Soul of the Duelist", "price": 250, "code": "SOD"},
    {"name": "Rise of Destiny", "price": 250, "code": "RDS"},
    {"name": "Flaming Eternity", "price": 250, "code": "FET"},
    {"name": "The Lost Millennium", "price": 250, "code": "TLM"},
    {"name": "Invasion of Chaos", "price": 300, "code": "IOC"},
    {"name": "Dark Beginning 1", "price": 300, "code": "DB1"},
    {"name": "Dark Beginning 2", "price": 300, "code": "DB2"},
    {"name": "Dark Revelation Volume 1", "price": 300, "code": "DR1"},
    {"name": "Cybernetic Revolution", "price": 300, "code": "CRV"},
    {"name": "The Duelist Genesis", "price": 300, "code": "TDGS"},
    {"name": "Phantom Darkness", "price": 300, "code": "PTDN"},
    {"name": "Gladiator's Assault", "price": 200, "code": "GLAS"},
    {"name": "Light of Destruction", "price": 200, "code": "LODT"},
]

PULL_RATES = {
    "guaranteed_slot": {
        "rare": 75.0,
        "super_rare": 25.0,
        "ultra_rare": 15.0,
        "secret_rare": 5.0,
        "ultimate_rare": 5.0,
    }
}

RARITIES = ["common", *PULL_RATES["guaranteed_slot"]]

GOAT_DEFAULT_PACKS = ["LOB", "MRD", "MRL", "PSV", "LON", "LOD", "IOC", "DB1", "DB2", "DR1"]
GOAT_DEFAULT_DPS = 10000

EDISON_DEFAULT_PACKS = ["MRD", "MRL", "IOC", "DR1", "CRV", "TDGS", "PTDN", "GLAS", "LODT"]
EDISON_DEFAULT_DPS = 20000

# El orden importa: "secret rare" y "normal rare" contienen "rare"
RARITY_KEYWORDS = [
    ("secret rare", "secret_rare"),
    ("ultimate rare", "ultimate_rare"),
    ("ultra rare", "ultra_rare"),
    ("super rare", "super_rare"),
    ("normal", "common"),
    ("rare", "rare"),
]


def normalize_rarity(rarity_str):
    r = rarity_str.lower()
    for keyword, rarity in RARITY_KEYWORDS:
        if keyword in r:
            return rarity
    return "common"


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_pools(cards, pack_code):
    pools = {rarity: set() for rarity in RARITIES}
    prefix = f"{pack_code}-"

    for card in cards:
        # Buscar la rareza por el prefijo del código del set (ej. "LOB-EN001")
        for s in card.get("card_sets", []):
            if s.get("set_code", "").upper().startswith(prefix):
                pools[normalize_rarity(s["set_rarity"])].add(card["id"])
                break
        else:
            # Si la API no detalla el código, la mandamos a common como resguardo
            pools["common"].add(card["id"])

    return {rarity: sorted(ids) for rarity, ids in pools.items()}


def generate_packs():
    os.makedirs(PACKS_DIR, exist_ok=True)
    available_packs = []

    for pack in PACKS_TO_FETCH:
        code = pack["code"]
        print(f"Obteniendo datos de: {code}...")

        try:
            response = requests.get(API_URL, params={"cardset": pack["name"]}, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code} en {code}. Ignorando.")
                continue

            pool = build_pools(response.json().get("data", []), code)

            write_json(os.path.join(PACKS_DIR, f"{code}.json"), {
                "id": code,
                "name": pack["name"],
                "price": pack["price"],
                "image": f"https://images.ygoprodeck.com/images/sets/{code}.jpg",
                "pool": pool,
            })

            available_packs.append(code)
            total = sum(len(ids) for ids in pool.values())
            print(f"  ✅ {code}.json creado con {total} cartas.")

        except Exception as e:
            print(f"❌ Error procesando {code}: {e}")

    # rules.json principal que actúa como índice
    write_json(OUTPUT_RULES, {
        "pull_rates": PULL_RATES,
        "available_packs": available_packs,
        "goat_recommended_packs": GOAT_DEFAULT_PACKS,
        "goat_recommended_dp": GOAT_DEFAULT_DPS,
        "edison_recommended_packs": EDISON_DEFAULT_PACKS,
        "edison_recommended_dp": EDISON_DEFAULT_DPS,
    })

    print("\n🎉 Proceso completado. Revisa la carpeta /packs/ y rules.json.")


if __name__ == "__main__":
    generate_packs()
