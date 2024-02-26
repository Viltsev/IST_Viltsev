import os
import asyncio
import uuid
from io import BytesIO
import httpx
from bs4 import BeautifulSoup
import requests
from PIL import Image
import logging
from context import ctx
import hashlib
from model.database import ImageData, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import base64
import psycopg2

# fetch urls
async def fetch(url):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    req = requests.get(url, headers, verify=False)
    src = req.text
    return src

# save image to a folder and database
async def saveImage(url, directory, db_session):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)

        if response.status_code == 200:
            imageName = str(uuid.uuid4()) + ".jpg"
            imagePath = os.path.join(directory, imageName)
            await compressImage(response.content, imagePath)

            # add image to database
            # get id for image
            imageId = hashlib.md5(response.content).hexdigest()
            # get base64 code for image
            imageBase64 = base64.b64encode(response.content).decode('utf-8')
            image = ImageData(id=imageId, data=imageBase64)
            db_session.add(image)
            logging.info("Image has been added to database successfully")


# load images from the page
async def loadPageImages(url, directory, imageCount, db_session):
    currentCount = imageCount
    html = await fetch(url)
    imageUrls = await scrapeImageURL(html)
    tasks = []
    for imgURL in imageUrls:
        # check: can we scrape images
        if len(tasks) < imageCount:
            tasks.append(saveImage(imgURL, directory, db_session))
            currentCount -= 1
    await asyncio.gather(*tasks)
    return currentCount


# image url scraper
async def scrapeImageURL(html):
    soup = BeautifulSoup(html, 'lxml')

    image_urls = [img['src'] for img in soup.find_all('img') if
                  (img['src'].startswith('http://') or img['src'].startswith('https://')) and img['src'].endswith(
                      '.jpg')]
    return image_urls

# image compressor
async def compressImage(imageContent, imagePath, quality=70, maxSize=1024 * 1024):
    if len(imageContent) > maxSize:
        with Image.open(BytesIO(imageContent)) as img:
            img.save(imagePath, optimize=True, quality=quality)
    else:
        with open(imagePath, 'wb') as f:
            f.write(imageContent)

async def crawler(startURL, directory, visitedUrls, imageCount, db_session):
    currentCount = imageCount
    # if we haven't visited the page
    if startURL not in visitedUrls:
        visitedUrls.add(startURL)

        # load images from the page
        currentCount = await loadPageImages(startURL, directory, imageCount, db_session)
    else:
        # else check the next pages
        logging.info(f"This page {startURL} has been visited! I'm going to the next page...")

    if currentCount > 0:
        html = await fetch(startURL)
        soup = BeautifulSoup(html, 'lxml')

        # checking the case when all pages have been scraped
        try:
            task = crawler("https://nos.twnsnd.co" + soup.find("a", class_="next").get("href"),
                           directory,
                           visitedUrls,
                           imageCount, db_session)
            await asyncio.gather(task)
        except Exception:
            return
    else:
        # save visited urls into the file
        with open("visitedURL.txt", "w") as f:
            f.write("\n".join(visitedUrls))
        logging.info("That's all images for scraping")
        return


async def main(startUrl, directory, imageCount: int, visitedUrls):
    engine = create_engine(ctx.database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    visitedURL = set()

    if os.path.exists("visitedURL.txt"):
        with open("visitedURL.txt", "r") as f:
            visitedURL = set(f.read().splitlines())

    # start the crawler
    await crawler(startUrl, directory, visitedURL, imageCount, session)
    session.commit()
    session.close()
