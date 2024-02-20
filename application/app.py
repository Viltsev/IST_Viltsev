import os
import asyncio
import uuid
from io import BytesIO
import httpx
from bs4 import BeautifulSoup
import requests
from PIL import Image

# fetch urls
async def fetch(url):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    req = requests.get(url, headers)
    src = req.text
    return src

# save image to a folder
async def saveImage(url, directory):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            imageName = str(uuid.uuid4()) + ".jpg"
            imagePath = os.path.join(directory, imageName)
            await compressImage(response.content, imagePath)


# load images from the page
async def loadPageImages(url, directory):
    html = await fetch(url)
    image_urls = await scrapeImageURL(html)
    tasks = [saveImage(img_url, directory) for img_url in image_urls]
    await asyncio.gather(*tasks)


# image url scraper
async def scrapeImageURL(html):
    soup = BeautifulSoup(html, 'lxml')

    image_urls = [img['src'] for img in soup.find_all('img') if (img['src'].startswith('http://') or img['src'].startswith('https://')) and img['src'].endswith('.jpg')]
    print(image_urls)
    return image_urls

# image compressor
async def compressImage(imageContent, imagePath, quality=70, maxSize=1024 * 1024):
    if len(imageContent) > maxSize:
        with Image.open(BytesIO(imageContent)) as img:
            img.save(imagePath, optimize=True, quality=quality)
    else:
        with open(imagePath, 'wb') as f:
            f.write(imageContent)


async def crawler(startURL, directory, visitedUrls):
    # if we haven't visited the page
    if startURL not in visitedUrls:
        visitedUrls.add(startURL)
        # save visited urls into the file
        with open("visitedURL.txt", "w") as f:
            f.write("\n".join(visitedUrls))

        # load images from the page
        await loadPageImages(startURL, directory)
    else:
        # else check the next pages
        print("this page has been visited! going to the next page...")


    html = await fetch(startURL)
    soup = BeautifulSoup(html, 'lxml')

    nextPage = soup.find("a", class_ = "next").get("href")
    nextPageUrl = "https://nos.twnsnd.co" + nextPage

    task = crawler(nextPageUrl, directory, visitedUrls)
    await asyncio.gather(task)


async def main():
    startURL = "https://nos.twnsnd.co/"
    # folder which saves our images
    directory = 'images'
    visitedURL = set()

    # if we already have visited urls
    if os.path.exists("visitedURL.txt"):
        with open("visitedURL.txt", "r") as f:
            visitedURL = set(f.read().splitlines())

    if not os.path.exists(directory):
        os.makedirs(directory)

    # start the crawler
    await crawler(startURL, directory, visitedURL)


if __name__ == "__main__":
    asyncio.run(main())