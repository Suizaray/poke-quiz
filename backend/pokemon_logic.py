import random
import requests

POKEAPI_BASE = "https://pokeapi.co/api/v2"

def get_pokemon_basic(poke_id):
    r = requests.get(f"{POKEAPI_BASE}/pokemon/{poke_id}")
    if r.status_code != 200:
        return None
    data = r.json()
    return {
        "name": data["name"].capitalize(),
        "id": data["id"],
        "types": [t["type"]["name"] for t in data["types"]],
        "base_stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
        "moves": [m["move"]["name"] for m in data["moves"]],
        "sprite": data["sprites"]["front_default"]
    }

def get_random_species(max_id=1025):
    poke_id = random.randint(1, max_id)
    return get_pokemon_basic(poke_id)

def random_evs_ivs():
    # Simple random EVs/IVs generator for 6 stats (hp, atk, def, spatk, spdef, speed)
    evs = {k: random.randint(0, 252) for k in ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]}
    # normalize EVs so total <= 510 (roughly)
    total = sum(evs.values())
    if total > 512:
        # scale down proportionally
        factor = 512 / total
        evs = {k: int(v * factor) for k, v in evs.items()}
    ivs = {k: random.randint(0, 31) for k in evs.keys()}
    return {"evs": evs, "ivs": ivs}

def pick_random_moves(move_pool, n=4):
    if not move_pool:
        return []
    unique = list(dict.fromkeys(move_pool))  # preserve order, dedupe
    if len(unique) <= n:
        return unique[:n]
    return random.sample(unique, n)

def generate_random_pokemon(owner_id=None, max_species_id=1025, level=None):
    """Return a dict representing a generated Pokemon (not ORM)."""
    species = get_random_species(max_species_id)
    if not species:
        raise RuntimeError("PokeAPI request failed")

    moves = pick_random_moves(species["moves"], n=4)
    ev_iv = random_evs_ivs()

    if level is None:
        level = random.randint(1, 100)
    pokemon = {
        "species_name": species["name"],
        "level": level,
        "stats": {
            "base_stats": species["base_stats"],
            "evs": ev_iv["evs"],
            "ivs": ev_iv["ivs"]
        },
        "moves": moves,
        "sprite_url": species.get("sprite")
    }
    return pokemon
