import torch
from library.mallampati_image_prep import prepare_loader
from library.mallampati_CNN_train_model import initialize_model, find_device


def load_model(device, model_path='mallampati_models/CNN models/model_mallampati_CNN_Best.pth'):
    """Load the pre-trained model and run predictions on the test set"""

    # Initialize the model
    model, optimizer, criterion = initialize_model()

    # Load the pre-trained model
    model.load_state_dict(torch.load(model_path, map_location=device))

    model.to(device)

    return model


def run_predictions_on_test_loader(model, test_loader, device):
    """Run predictions on the test set and print the total accuracy"""

    model.eval()  # Set the model to evaluation mode
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    print(f"Total Accuracy: {accuracy:.2f}%")


def run_predictions_on_image(model, image, device):
    """Run predictions on a single image from the pipeline and return the predicted class"""

    model.eval()  # Set the model to evaluation mode

    with torch.no_grad():
        image = image.to(device)
        output = model(image)
        _, predicted = torch.max(output.data, 1)

        return predicted


if __name__ == '__main__':
    # Find the device
    device = find_device()

    # Load the model and move to device
    model = load_model(device)

    # Prepare the test data
    test_loader = prepare_loader(path='mallampati_datasets/test_data(ManualSplit)', image_pixel_size=64)

    # Run predictions
    run_predictions_on_test_loader(model, test_loader, device)
