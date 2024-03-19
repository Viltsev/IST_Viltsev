from fastapi import FastAPI
from machineLearning.context import ctx
from contextlib import asynccontextmanager
from machineLearning import delete_duplications
from machineLearning import background_deletion
from machineLearning import background_insertion
from machineLearning import find_similar_color
from machineLearning import clip_finder
from machineLearning import find_complementary
from machineLearning import find_images


@asynccontextmanager
async def lifespan(app: FastAPI):
    ctx.make_images_without_background()
    ctx.make_images_with_background()
    ctx.make_similar_complementary_color()
    ctx.make_similar_colors()
    ctx.make_similar_images()

    yield

app = FastAPI(lifespan=lifespan)

@app.post("/delete_duplicate")
async def deleteDuplicates():
    await delete_duplications.main(ctx.imagesDir)
    return {"message": "duplications have been deleted"}

@app.post("/background_deletion")
async def backgroundDeletion():
    await background_deletion.delete_background(ctx.imagesDir, ctx.images_without_background)
    return {"message": "background has been deleted"}

@app.post("/background_insertion")
async def backgroundInsertion(imageCount: int):
    await background_insertion.background_insertion(ctx.images_with_background,
                                                    imageCount,
                                                    ctx.images_without_background,
                                                    ctx.background_image)

    return {"message": "background has been inserted"}

@app.post("/find_similar_by_color")
async def findSimilarByColor(red: int, green: int, blue: int):
    await find_similar_color.search_image(red, green, blue, ctx.images_without_background, ctx.similar_colors)
    return {"message": "similar images have been found"}

@app.post("/find_complementary_by_color")
async def findComplementaryByColor(red: int, green: int, blue: int):
    await find_complementary.search_image(red, green, blue, ctx.images_without_background,
                                          ctx.similar_complementary_color)
    return {"message": "complementary images have been found"}

@app.post("/find_image_by_text")
async def findImageByText(searchByText: str):
    await clip_finder.main(searchByText, ctx.images_without_background, ctx.clip_output_folder)
    return {"message": "images have been found"}

@app.post("/find_similar_images")
async def findSimilarImages():
    await find_images.main(ctx.source_image, ctx.images_without_background, ctx.similar_images)
    return {"message": "similar images have been found"}