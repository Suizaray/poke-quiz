from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .database import SessionLocal
from .models import Player, Pokemon
from .pokemon_logic import generate_random_pokemon

router = APIRouter()

class BuyRequest(BaseModel):
    player_id: int

@router.post("/buy")
def buy_random_pokemon(req: BuyRequest):
    db = SessionLocal()
    player = db.query(Player).filter(Player.id == req.player_id).first()
    if not player:
        db.close()
        raise HTTPException(status_code=404, detail="Player not found")
    COST = 10
    if player.total_points < COST:
        db.close()
        raise HTTPException(status_code=400, detail="Not enough points")
    # Deduct cost
    player.total_points -= COST

    # Generate a random pokemon (dict)
    gen = generate_random_pokemon(owner_id=player.id)
    new_poke = Pokemon(
        owner_id=player.id,
        species_name=gen["species_name"],
        level=gen["level"],
        stats=gen["stats"],
        moves=gen["moves"],
        sprite_url=gen["sprite_url"]
    )
    db.add(new_poke)
    db.commit()
    db.refresh(new_poke)
    response = {
        "id": new_poke.id,
        "species_name": new_poke.species_name,
        "level": new_poke.level,
        "moves": new_poke.moves,
        "stats": new_poke.stats,
        "sprite_url": new_poke.sprite_url,
        "player_points": player.total_points
    }
    db.close()
    return response
