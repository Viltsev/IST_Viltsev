from fastapi import FastAPI

import scraper

app = FastAPI()

@app.post("/imageCount")
async def scrapeImages(imageCount: int):
    await scraper.main(imageCount)
    return {"message": "scraping complete"}