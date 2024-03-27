import os
from PIL import Image, UnidentifiedImageError
import imagehash
import logging


async def find_duplicates(directory):
    # make empty dictionary to save hash of images and paths to duplicates
    hash_dict = {}
    duplicate_images = {}

    # check all files in the next directory
    for filename in os.listdir(directory):
        # check if file is file (not directory)
        if os.path.isfile(os.path.join(directory, filename)):
            # make full path to the file
            image_path = os.path.join(directory, filename)
            try:
                # try to open image with PIL library
                with Image.open(image_path) as img:
                    # get hash of the image
                    hash_value = str(imagehash.phash(img))
                    # check if we have the same hash in dictionary
                    if hash_value in hash_dict:
                        # if we have the same hash, so we have duplicate
                        # get path to the original image
                        original_image = hash_dict[hash_value]
                        # check, if we have this original image in duplicates list
                        if original_image in duplicate_images:
                            # if we have -> append path for duplicate list of this original image
                            duplicate_images[original_image].append(image_path)
                        else:
                            # if we don't have -> make new in dictionary
                            duplicate_images[original_image] = [image_path]
                    else:
                        # if we don't have this hash in dictionary -> append it
                        hash_dict[hash_value] = image_path
            except UnidentifiedImageError:
                logging.info(f"Can not to read image: {image_path}")
    # return dictionary of duplicates
    return duplicate_images


async def delete_duplicates(duplicate_dict, index_to_delete):
    # check every pair in duplicates dictionary
    for original_image, duplicates in duplicate_dict.items():
        # check if the index doesn't go beyond the list of duplicates
        if index_to_delete < len(duplicates):
            # get path to duplicate by index
            path_to_delete = duplicates[index_to_delete]
            # check if file exists
            if os.path.exists(path_to_delete):
                # delete file
                os.remove(path_to_delete)
                logging.info(f"Удален дубликат: {path_to_delete}")
            else:
                logging.info(f"Файл для удаления не найден: {path_to_delete}")
                break


async def main(directory):
    duplicates = await find_duplicates(directory)
    await delete_duplicates(duplicates, 0)
