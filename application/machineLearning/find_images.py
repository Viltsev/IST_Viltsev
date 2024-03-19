import torch
import clip
from PIL import Image
import os
import logging

# Load the CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
result = {}

def load_image(file_path):
    image = Image.open(file_path)
    image = preprocess(image).unsqueeze(0).to(device)
    return image

def calculate_clip_similarity(target_image, image):
    with torch.no_grad():
        image_features = model.encode_image(image)
        target_features = model.encode_image(target_image)
        cos = torch.nn.CosineSimilarity(dim=0)
        sim = cos(image_features[0], target_features[0]).item()
        sim = (sim + 1) / 2
    return sim

def find_similar_images(target_image_path, folder_path):
    target_image = load_image(target_image_path)
    similar_images = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(folder_path, file_name)
            image = load_image(image_path)
            similarity = calculate_clip_similarity(target_image, image)
            similar_images.append((image_path, similarity))

    similar_images.sort(key=lambda x: x[1], reverse=True)
    return similar_images[:5]

def save_similar_images(similar_images, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, (image_path, _) in enumerate(similar_images):
        image_name = os.path.basename(image_path)
        new_image_path = os.path.join(output_folder, f"similar_{i+1}_{image_name}")
        image = Image.open(image_path)
        image.save(new_image_path)

source_image = "imagesWithoutBackground/693580eeae135ee71a39dbe8e3237bb1.png"
source_directory = "imagesWithoutBackground"
output_directory = "./similarImages"
similar_images = find_similar_images(source_image, source_directory)

if similar_images:
    save_similar_images(similar_images, output_directory)
else:
    logging.info("There are no similar images")