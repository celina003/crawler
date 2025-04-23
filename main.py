import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from jobs.scraper import scrape_jobs

# Logging-Konfiguration
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()  # <- Diese Zeile bleibt

# CORS-Middleware hinzufügen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Arbeitsagentur Scraper läuft!"}

@app.get("/jobs")
async def get_jobs():
    try:
        jobs = await scrape_jobs()
        return {"jobs": jobs}
    except Exception as e:
        logging.error(f"Fehler beim Scrapen der Jobs: {e}")
        return {"error": str(e)}

