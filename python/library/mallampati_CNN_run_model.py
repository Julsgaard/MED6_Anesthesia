import torch
from library.mallampati_image_prep import prepare_test_loader
from library.mallampati_CNN_train_model import initialize_model


def load_model(device, model_path='mallampati_models/CNN models/model_mallampati_CNN_20240503_205354.pth'):
    """Load the pre-trained model and run predictions on the test set"""

    # Initialize the model
    model, optimizer, criterion = initialize_model()

    # Load the pre-trained model
    model.load_state_dict(torch.load(model_path))

    model.to(device)

    return model


def find_device():
    """Find the device to run the model on"""

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    return device


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
    test_loader = prepare_test_loader(image_pixel_size=64, path='mallampati_datasets/New Test')

    # Run predictions
    run_predictions_on_test_loader(model, test_loader, device)
