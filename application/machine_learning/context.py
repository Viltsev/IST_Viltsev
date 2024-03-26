import os


class Context:
    imagesDir = "images"
    images_without_background = "imagesWithoutBackground"
    images_with_background = 'imagesWithBackground'
    clip_output_folder = "clipResults"
    background_image = "background.jpg"
    similar_colors = "similarColors"
    similar_complementary_color = "similarComplementaryColor"
    source_image = "imagesWithoutBackground/693580eeae135ee71a39dbe8e3237bb1.png"
    similar_images = "./similarImages"

    def make_images_without_background(self):
        if not os.path.exists(self.images_without_background):
            os.makedirs(self.images_without_background)

    def make_images_with_background(self):
        if not os.path.exists(self.images_with_background):
            os.makedirs(self.images_with_background)

    def make_similar_complementary_color(self):
        if not os.path.exists(self.similar_complementary_color):
            os.makedirs(self.similar_complementary_color)

    def make_similar_colors(self):
        if not os.path.exists(self.similar_colors):
            os.makedirs(self.similar_colors)

    def make_similar_images(self):
        if not os.path.exists(self.similar_images):
            os.makedirs(self.similar_images)



ctx = Context()
