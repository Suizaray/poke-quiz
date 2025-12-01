from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .database import SessionLocal
from .models import Player
from .pokemon_logic import get_random_species
import random
import json
import re
from shared import openai_client

router = APIRouter()

class QuizQuestion(BaseModel):
    question: str
    options: list
    answer: str
    hint: str
    pokemon_id: int = None

def local_quiz():
    # Safe fallback: pick species and create multiple choice using PokeAPI names
    correct = get_random_species()
    wrong = []
    while len(wrong) < 3:
        p = get_random_species()
        if p and p["name"] != correct["name"] and p["name"] not in wrong:
            wrong.append(p["name"])
    options = wrong + [correct["name"]]
    random.shuffle(options)
    q = f"Which Pokémon is {correct['name']}?"
    return {
        "question": q,
        "options": options,
        "answer": correct["name"],
        "hint": f"Types: {', '.join(correct['types'])}",
        "pokemon_id": correct["id"]
    }

@router.get("/quiz")
def get_quiz():
    # If OPENAI_API_KEY present, attempt to call OpenAI for a prettier question.
    try:
        
        if openai_client.client:
            correct = get_random_species()
            wrong = []
            while len(wrong) < 3:
                p = get_random_species()
                if p and p["name"] != correct["name"] and p["name"] not in wrong:
                    wrong.append(p["name"])
            options = wrong + [correct["name"]]
            random.shuffle(options)
            prompt = f"""
                    You are a Pokémon Quizmaster.
                    Create a multiple-choice question with **one correct answer** and three wrong options.
                    Correct answer: {correct['name']}
                    Options: {options}
                    Include a short hint about the Pokémon without giving away the answer.

                    **IMPORTANT: Return ONLY valid JSON with EXACT keys:**
                    - question (string)
                    - options (list of 4 strings)
                    - answer (string)
                    - hint (string)

                    Do not include any text outside the JSON.
                        """
            
            response = openai_client.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
            )
            text = response.choices[0].message.content.strip()

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                print("DEBUG → JSON decode error, trying regex")
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                else:
                    print("DEBUG → JSON regex extraction FAILED")
                    raise
            data["pokemon_id"] = correct["id"]
            print("DEBUG → FINAL QUIZ DATA:", data)
            return data
    except Exception as e:
        print("DEBUG → Hard error:", e)
    print("DEBUG → Falling back to local quiz")
    return local_quiz()


class AwardPointsRequest(BaseModel):
    player_id: int
    points: int

@router.post("/award_points")
def award_points(req: AwardPointsRequest):
    db = SessionLocal()
    player = db.query(Player).filter(Player.id == req.player_id).first()
    if not player:
        db.close()
        raise HTTPException(status_code=404, detail="Player not found")
    
    player.total_points += req.points
    db.commit()
    db.refresh(player)
    points = player.total_points
    db.close()
    return {"player_id": player.id, "total_points": points}
