
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import requests
from groq import Groq

app = FastAPI(title="SEO Brief Generator API (Canlı SERP Destekli)", version="2.0")

# --- API ANAHTARLARINI BURAYA YAZIN ---
GROQ_KEY = os.getenv("GROQ_KEY")
import os
from dotenv import load_dotenv

load_dotenv()
SERPER_KEY = os.getenv("SERPER_KEY")

# Groq İstemcisini başlatıyoruz
client = Groq(api_key=GROQ_KEY)

# --- INPUT (Girdi) MODELİ ---
class BriefRequest(BaseModel):
    keyword: str = Field(..., example="en iyi basketbol ayakkabıları")
    language: str = Field(default="Turkish", example="Turkish")
    target_audience: str = Field(default="Genel Okuyucu", example="Sporcular")

# --- GOOGLE ARAMA FONKSİYONU (SERPER) ---
def get_live_google_results(query: str):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "gl": "tr", "hl": "tr"})
    headers = {
        'X-API-KEY': SERPER_KEY,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        results = response.json()
        
        # İlk 5 rakibin başlık ve özet bilgisini topluyoruz
        competitor_data = []
        for item in results.get("organic", [])[:5]:
            competitor_data.append(f"Başlık: {item.get('title')}\nÖzet: {item.get('snippet')}\n---")
        
        return "\n".join(competitor_data)
    except Exception:
        return "Canlı Google verisi alınamadı."

# --- ENDPOINT ---
@app.post("/api/v1/generate-brief")
async def generate_seo_brief(request: BriefRequest):
    try:
        # 1. Adım: Google'dan canlı verileri çek
        live_data = get_live_google_results(request.keyword)

        # 2. Adım: Yapay zekaya talimatı hazırla
        system_instruction = (
            "Sen kıdemli bir SEO Stratejistisin. Kullanıcının verdiği anahtar kelimeyi ve sana sunulan "
            "canlı Google arama sonuçlarındaki (rakip analizleri) verileri inceleyerek kapsamlı bir SEO içerik briefi hazırlamalısın.\n"
            "Yanıtını MUTLAKA sadece ve sadece geçerli bir JSON objesi olarak dön. Markdown işaretleri (```json gibi) ekleme.\n\n"
            "İstenen JSON Yapısı:\n"
            "{\n"
            "  \"recommended_title\": \"string\",\n"
            "  \"meta_description\": \"string\",\n"
            "  \"search_intent\": \"string\",\n"
            "  \"target_word_count\": 1500,\n"
            "  \"primary_keywords\": [\"string\"],\n"
            "  \"secondary_keywords\": [\"string\"],\n"
            "  \"suggested_outline\": [\n"
            "    {\"tag\": \"H2\", \"title\": \"string\", \"notes_for_writer\": \"string\"}\n"
            "  ],\n"
            "  \"eeat_recommendations\": [\"string\"]\n"
            "}"
        )

        user_prompt = (
            f"Anahtar Kelime: {request.keyword}\n"
            f"Dil: {request.language}\n"
            f"Hedef Kitle: {request.target_audience}\n\n"
            f"--- CANLI GOOGLE ARAMA SONUÇLARI (RAKİPLER) ---\n"
            f"{live_data}\n\n"
            f"Yukarıdaki rakipleri analiz ederek onları geçecek bir brief üret."
        )

        # 3. Adım: Groq Llama 3'ü çağır
        completion = client.chat.completions.create(
          model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        response_content = completion.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)