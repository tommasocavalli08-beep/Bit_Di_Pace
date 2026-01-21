from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests

API_KEY = "4b343ffcd5f34c2f9e4366f80bc33f74.HVAAdJLUzPjH2tVX0s9vsAxk"
MODEL = "cogito-2.1:671b"

app = FastAPI()

class TextIn(BaseModel):
    text: str

def ollama_chat_simple(message: str):
    url = "https://ollama.com/api/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "max_tokens": 500,
        "stream": False
    }

    res = requests.post(url, json=data, headers=headers, timeout=20)
    res.raise_for_status()
    result = res.json()
    if "message" in result:
        return result["message"]["content"]
    return result.get("response", "Errore nella risposta")

@app.get("/", response_class=HTMLResponse)
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/api")
def api(data: TextIn):
    # 1) Pacifica la frase in italiano
    stringHeader = (
        "ti passo una frase che potrebbe contenere qualcosa di offensivo/aggressivo. "
        "trasformala in qualcosa di più pacifico ma senza alterarne il contenuto. "
        "rispondi solo con la frase prodotta senza nessun proemio."
    )
    user_input = stringHeader + "\n" + data.text
    italian_result = ollama_chat_simple(user_input)

    # 2) Traduci in inglese
    translation_header_en = (
        "Ora traduci la frase qui sotto in inglese. "
        "Rispondi solo con la traduzione, senza spiegazioni."
    )
    english_result = ollama_chat_simple(translation_header_en + "\n" + italian_result)

    # 3) Traduci in portoghese (Brasile)
    translation_header_pt = (
        "Agora traduza a frase abaixo para o português do Brasil. "
        "Responda apenas com a tradução, sem explicações."
    )
    portuguese_result = ollama_chat_simple(translation_header_pt + "\n" + italian_result)

    return {
        "italian": italian_result,
        "english": english_result,
        "portuguese": portuguese_result
    }
