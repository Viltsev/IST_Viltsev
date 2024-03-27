import torch
import clip
from PIL import Image
import os
import logging


async def load_image(file_path, preprocess, device):
    image = Image.open(file_path)
    image = preprocess(image).unsqueeze(0).to(device)
    return image

async def calculate_clip_similarity(target_image, image, model):
    with torch.no_grad():
        image_features = model.encode_image(image)
        target_features = model.encode_image(target_image)
        cos = torch.nn.CosineSimilarity(dim=0)
        sim = cos(image_features[0], target_features[0]).item()
        sim = (sim + 1) / 2
    return sim

async def find_similar_images(target_image_path, folder_path, preprocess, device, model):
    target_image = await load_image(target_image_path, preprocess, device)
    similar_images = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(folder_path, file_name)
            image = load_image(image_path)
            similarity = await calculate_clip_similarity(target_image, image, model)
            similar_images.append((image_path, similarity))

    similar_images.sort(key=lambda x: x[1], reverse=True)
    return similar_images[:5]

async def save_similar_images(similar_images, output_folder):
    for i, (image_path, _) in enumerate(similar_images):
        image_name = os.path.basename(image_path)
        new_image_path = os.path.join(output_folder, f"similar_{i+1}_{image_name}")
        image = Image.open(image_path)
        image.save(new_image_path)


async def main(source_image, source_directory, output_directory):
    # Load the CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    similar_images = await find_similar_images(source_image, source_directory, preprocess, device, model)

    if similar_images:
        await save_similar_images(similar_images, output_directory)
    else:
        logging.info("There are no similar images")
