from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .database import SessionLocal
from .models import Player
from .pokemon_logic import generate_random_pokemon
import random
import json
from shared import openai_client

router = APIRouter()

@router.get("/generate_opponent")
def generate_opponent():
    try:
        # Generate 6 random Pokémon as opponent team
        opponent_team = []
        for i in range(6):
            poke = generate_random_pokemon()   # returns dict/JSON
            poke["id"] = -(i+1)
            poke["in_party"] = i + 1           # give them slot ordering
            opponent_team.append(poke)

        battle_state = {
            "opponent_team": opponent_team,
            "status": "in_progress",
            "turn": 1
        }

        return battle_state

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/opponent_choose")
def opponent_choose(payload: dict):
    opponent_team = payload.get("opponent_team", [])
    player_team = payload.get("player_team", [])
    player_selected = payload.get("player_selected")

    if not opponent_team or not player_selected:
        raise HTTPException(status_code=400, detail="Missing team data")

    # Basic AI logic (placeholder for LLM usage)
    # You can later replace this with openai_client reasoning:
    # chosen = openai_client.smart_choice(player, opponent_team)
    available = [p for p in opponent_team if not p.get("fainted", False)]
    chosen = random.choice(available)

    return {"opponent_selected": chosen}
