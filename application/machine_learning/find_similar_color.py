import os
import cv2
import numpy as np
import logging
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor
from colormath.color_conversions import convert_color

def asscalar_method(a):
    return a.item()

async def calculate_average_color(image):
    # Calculate average color in rectangle
    averageColor = np.mean(image, axis=(0, 1))
    return LabColor(averageColor[0], averageColor[1], averageColor[2])

# Search similar images by color
async def search_similar_colors(query_color, average_colors):
    similarities = []
    for color in average_colors:
        similarity = delta_e_cie2000(query_color, color)
        similarities.append(similarity)
    return similarities

# Find similar images by color (main method)
async def search_image(r, g, b, imageDirectory, outputDirectory):
    setattr(np, "asscalar", asscalar_method)

    # Load images and calculate their averages colors
    imageFiles = os.listdir(imageDirectory)
    imagePaths = [os.path.join(imageDirectory, f) for f in imageFiles]
    images = []
    averageColors = []
    for image_path in imagePaths:
        image = cv2.imread(image_path)
        images.append(image)
        averageColor = await calculate_average_color(image)
        averageColors.append(averageColor)

    # RGB to Lab
    rgbColor = np.array([r, g, b], dtype=np.uint8)
    sourceColor = LabColor(rgbColor[2], rgbColor[1], rgbColor[0])
    labColor = convert_color(sourceColor, LabColor)

    queryColor = LabColor(labColor.lab_l, labColor.lab_a, labColor.lab_b)
    similarities = await search_similar_colors(queryColor, averageColors)

    # amount of similar images
    amountImages = 5
    similarImagesInx = np.argsort(similarities)[:amountImages]

    for idx in similarImagesInx:
        image_filename = os.path.join(outputDirectory, f'similar_image_{idx}.jpg')
        cv2.imwrite(image_filename, images[idx])
        logging.info(f'Saved similar image {idx} to {image_filename}')
