from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .database import init_db
from .shop import router as shop_router
from .quiz import router as quiz_router
from .battle import router as battle_router
from .models import Player, Pokemon
from .database import SessionLocal

app = FastAPI(title="Pokémon Game Backend")

@app.on_event("startup")
def startup():
    init_db()

@app.post("/players")
def create_player(username: str):
    db = SessionLocal()
    existing = db.query(Player).filter(Player.username == username).first()
    if existing:
        res = {"id": existing.id, "username": existing.username, "total_points": existing.total_points}
        db.close()
        return res
    new = Player(username=username, total_points=0)
    db.add(new)
    db.commit()
    db.refresh(new)
    res = {"id": new.id, "username": new.username, "total_points": new.total_points}
    db.close()
    return res

@app.get("/players/{player_id}")
def get_player(player_id: int):
    db = SessionLocal()
    p = db.query(Player).filter(Player.id == player_id).first()
    if not p:
        db.close()
        return {"error": "player not found"}
    res = {"id": p.id, "username": p.username, "total_points": p.total_points}
    db.close()
    return res

@app.get("/players/{player_id}/pokemon")
def get_player_pokemon(player_id: int):
    db = SessionLocal()
    try:
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        # return Pokémon with in_party info
        pokemon_list = []
        for p in player.pokemon:
            pokemon_list.append({
                "id": p.id,
                "species_name": p.species_name,
                "level": p.level,
                "stats": p.stats,
                "moves": p.moves,
                "sprite_url": p.sprite_url,
                "in_party": p.in_party   # 0 = not in party, 1-6 = party slot
            })
        return pokemon_list
    finally:
        db.close()


class PartySlotRequest(BaseModel):
    slot: int  # 1-6

@app.post("/players/{player_id}/pokemon/{poke_id}/set_party_slot")
def set_party_slot(player_id: int, poke_id: int, req: PartySlotRequest):
    if req.slot < 0 or req.slot > 6:
        raise HTTPException(status_code=400, detail="Slot must be between 0 and 6")
    
    db = SessionLocal()
    try:
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        pokemon = db.query(Pokemon).filter(Pokemon.id == poke_id, Pokemon.owner_id == player_id).first()
        if not pokemon:
            raise HTTPException(status_code=404, detail="Pokemon not found")
        
        # Check if another Pokémon already occupies this slot
        if req.slot != 0:
            existing = db.query(Pokemon).filter(Pokemon.owner_id == player_id, Pokemon.in_party == req.slot).first()
            if existing:
                # swap them out to PC (0)
                existing.in_party = 0
        
        # assign this Pokémon to the slot
        pokemon.in_party = req.slot
        db.commit()
        db.refresh(pokemon)
        return {
            "id": pokemon.id,
            "species_name": pokemon.species_name,
            "slot": pokemon.in_party
        }
    finally:
        db.close()

app.include_router(shop_router, prefix="/shop")
app.include_router(quiz_router, prefix="/quiz")
app.include_router(battle_router, prefix="/battle")
