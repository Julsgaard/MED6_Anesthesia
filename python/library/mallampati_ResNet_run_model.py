import os
import torch
from torch import nn
from torchvision import models, transforms
from PIL import Image
from library.mallampati_image_prep import prepare_loader


def load_model_ResNet(device, model_path='mallampati_models/loss_0.0183_1000_epochs/model.pth'):
    """Load the pre-trained ResNet model"""

    # Initialize the model
    model = models.resnet34(weights='ResNet34_Weights.DEFAULT')
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(512, 2)
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

    with open(output_file, 'w') as file:
        for image_name in os.listdir(folder_path):
            image_path = os.path.join(folder_path, image_name)
            if os.path.isfile(image_path):
                image = process_image(image_path, image_size)  # Process the image
                image = image.unsqueeze(0)  # Add batch dimension
                prediction = run_predictions_on_image(model, image, device)
                file.write(f"{image_name}: {prediction}\n")


if __name__ == '__main__':
    # Set the device to GPU if available
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Load the model and move to device
    model_path = 'mallampati_models/loss_0.0183_1000_epochs/model.pth'
    model = load_model_ResNet(device, model_path)

    # Parameters
    test_folder_path = 'mallampati_datasets/KatrineBilleder'
    output_file_path = 'predictions.txt'
    image_size = 64  # Assuming the image size used in training

    # Run predictions on all images in the folder and save to file
    run_predictions_on_folder(model, test_folder_path, device, output_file_path, image_size)

    print(f"Predictions saved to {output_file_path}")
