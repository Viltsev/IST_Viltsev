import io
import os
import keras
import numpy as np
from PIL import Image

async def predict_image_class(uploaded_image):
    model_save_path = os.path.join(os.path.dirname(__file__), "new_model_training.h5")
    loaded_model = keras.models.load_model(model_save_path)

    loaded_model.compile(optimizer='adam',
                         loss='sparse_categorical_crossentropy',
                         metrics=['accuracy'])

    image = Image.open(io.BytesIO(uploaded_image))
    image = image.resize((224, 224))
    image_array = np.array(image)

    # Data normalization
    image_array = image_array / 255.0
    # Add batch size
    image_array = np.expand_dims(image_array, axis=0)
    predictions = loaded_model.predict(image_array)

    predictions_in_percentage = np.array([format(prob * 100, '.2f') for prob in predictions[0]])
    classes_with_percent = {"pants": predictions_in_percentage[0],
                            "sweater": predictions_in_percentage[1],
                            "shorts": predictions_in_percentage[2],
                            "t-shirts": predictions_in_percentage[3],
                            }

    return classes_with_percent