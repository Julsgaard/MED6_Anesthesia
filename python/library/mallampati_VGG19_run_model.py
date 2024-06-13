import os
import torch
from torch import nn
from torchvision import models, transforms
from PIL import Image
from library.mallampati_image_prep import prepare_loader

def load_model_VGG19(device, model_path='mallampati_models/VGG19_models/loss_0.0463_8_epochs/model.pth'):
    """Load the pre-trained VGG19 model"""

    # Initialize the model
    model = models.vgg19(weights='VGG19_Weights.DEFAULT')
    num_features = model.classifier[0].in_features
    model.classifier = nn.Sequential(
        nn.Linear(num_features, 4096),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(4096, 4096),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(4096, 2)
    )

    # Load the pre-trained model
    model.load_state_dict(torch.load(model_path, map_location=device))

    model.to(device)

    return model

def process_image(image_path, image_size):
    """Process a single image for model prediction"""
    transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    image = Image.open(image_path).convert('RGB')  # Assuming RGB images
    image = transform(image)
    return image

def run_predictions_on_image(model, image, device):
    """Run predictions on a single image from the pipeline and return the predicted class"""

    model.eval()  # Set the model to evaluation mode

    with torch.no_grad():
        image = image.to(device)
        output = model(image)
        _, predicted = torch.max(output.data, 1)

    return predicted.item()

def run_predictions_on_folder(model, folder_path, device, output_file, image_size):
    """Run predictions on all images in a folder and save the predictions to a text file"""

    model.eval()  # Set the model to evaluation mode

    # Map model predictions to the desired output format
    prediction_mapping = {0: "1+2", 1: "3+4"}

    with open(output_file, 'w') as file:
        for image_name in os.listdir(folder_path):
            image_path = os.path.join(folder_path, image_name)
            if os.path.isfile(image_path):
                image = process_image(image_path, image_size)  # Process the image
                image = image.unsqueeze(0)  # Add batch dimension
                prediction = run_predictions_on_image(model, image, device)
                mapped_prediction = prediction_mapping[prediction]
                file.write(f"{image_name}: {mapped_prediction}\n")

if __name__ == '__main__':
    # Set the device to GPU if available
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Load the model and move to device
    model_path = 'mallampati_models/VGG19_models/loss_0.0463_8_epochs/model.pth'
    model = load_model_VGG19(device, model_path)

    # Parameters
    test_folder_path = 'mallampati_datasets/CroppedImagesKatrine'
    output_file_path = 'predictions.txt'
    image_size = 64  # Assuming the image size used in training

    # Run predictions on all images in the folder and save to file
    run_predictions_on_folder(model, test_folder_path, device, output_file_path, image_size)

    print(f"Predictions saved to {output_file_path}")
