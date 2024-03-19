import os
import cv2
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor
from colormath.color_conversions import convert_color
import numpy as np


def asscalar_method(a):
    return a.item()


async def calculate_average_color(image):
    # Calculate average color in rectangle
    averageColor = np.mean(image, axis=(0, 1))
    return LabColor(averageColor[0], averageColor[1], averageColor[2])

# Search most similar images by color
async def search_similar_colors(query_color, average_colors):
    similarities = []
    for color in average_colors:
        similarity = delta_e_cie2000(query_color, color)
        similarities.append(similarity)
    return similarities

def search_image(r, g, b, imageDir, outputDirectory):
    setattr(np, "asscalar", asscalar_method)

    # Load images and calculating their averages colors
    imageFiles = os.listdir(imageDir)
    imagePaths = [os.path.join(imageDir, f) for f in imageFiles]
    images = []
    averageColors = []
    for image_path in imagePaths:
        image = cv2.imread(image_path)
        images.append(image)
        averageColor = await calculate_average_color(image)
        averageColors.append(averageColor)

    # RGB to HSV
    rgbColor = np.uint8([[[r, g, b]]])
    hsvColor = cv2.cvtColor(rgbColor, cv2.COLOR_RGB2HSV)

    # Calculate complementary hue
    complementaryHue = (hsvColor[0][0][0] + 180) % 360

    # Complementary hue to RGB
    complementary_hsv_color = np.uint8([[[complementaryHue, 255, 255]]])
    complementary_rgb_color = cv2.cvtColor(complementary_hsv_color, cv2.COLOR_HSV2RGB)
    comp_r, comp_g, comp_b = complementary_rgb_color[0][0]

    # Complementary RGB to Lab
    labColor = convert_color(LabColor(comp_b, comp_g, comp_r), LabColor)
    queryColor = LabColor(labColor.lab_l, labColor.lab_a, labColor.lab_b)
    similarities = await search_similar_colors(queryColor, averageColors)

    amountImages = 5
    similarImagesInx = np.argsort(similarities)[:amountImages]

    for idx in similarImagesInx:
        image_filename = os.path.join(outputDirectory, f'similar_image_{idx}.png')
        cv2.imwrite(image_filename, images[idx])