import torch
from library.mallampati_image_prep import prepare_test_data
from library.mallampati_CNN_train_model import create_layers, initialize_model


def run_predictions(model, test_loader):
    """Run predictions on the test set and print the total accuracy"""
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


if __name__ == '__main__':
    # Create the layers for the CNN
    layers = create_layers()

    # Initialize the model
    model, optimizer, criterion = initialize_model(layers)

    # Load the pre-trained model
    model.load_state_dict(torch.load('mallampati_models/CNN models/model_mallampati_CNN_20240502_000217.pth'))

    # Move the model to the device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # Move the model to the device
    model.to(device)

    # Set the model to evaluation mode
    model.eval()

    # Prepare the test data
    test_loader = prepare_test_data('mallampati_datasets/mallampati_training_data (2 classes)')

    # Run predictions
    run_predictions(model, test_loader)
