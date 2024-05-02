import datetime
import torch
import torch.nn as nn
import torch.optim as optim
from library.mallampati_image_prep import prepare_image_data, prepare_training_and_validation_data


def create_layers():
    """Function to create a dictionary of layers for the CNN"""
    layers = {
        'conv1': nn.Conv2d(3, 32, kernel_size=3, padding=1),  # 3 input channels for RGB images
        'conv2': nn.Conv2d(32, 64, kernel_size=3, padding=1),  # 32 input channels from the previous layer
        'conv3': nn.Conv2d(64, 128, kernel_size=3, padding=1),  # 64 input channels from the previous layer
        'pool': nn.MaxPool2d(2, 2),  # Max pooling layer with a kernel size of 2 and stride of 2
        'relu': nn.ReLU(),  # ReLU activation function
        'flatten': nn.Flatten(),  # Flatten layer to convert 2D data to 1D for the fully connected layers
        'fc1': nn.Linear(128 * 28 * 28, 512),  # 128 channels from the last conv layer, 28x28 image size
        'fc2': nn.Linear(512, 2)  # 512 input features from the previous layer
    }
    return layers


def initialize_model(layers):
    """Function to initialize the model, optimizer, and loss function for training"""

    model = nn.Sequential(
        layers['conv1'],
        layers['relu'],
        layers['pool'],
        layers['conv2'],
        layers['relu'],
        layers['pool'],
        layers['conv3'],
        layers['relu'],
        layers['pool'],
        layers['flatten'],
        layers['fc1'],
        layers['relu'],
        layers['fc2']
    )
    optimizer = optim.Adam(model.parameters(), lr=0.001)  # Using Adam optimizer
    criterion = nn.CrossEntropyLoss()  # Cross-entropy loss
    return model, optimizer, criterion


def train_model(model, train_loader, validation_loader, criterion, optimizer, device, num_epochs=25):
    """Train the model using the training and validation data loaders for a specified number of epochs."""

    model.to(device)  # Move the model to the GPU if available

    for epoch in range(num_epochs):
        model.train()  # Set model to training mode
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)  # Move images and labels to the device (GPU or CPU)
            optimizer.zero_grad()  # Zero the parameter gradients
            outputs = model(images)  # Forward pass: compute the predicted outputs by passing inputs to the model
            loss = criterion(outputs, labels)  # Compute loss
            loss.backward()  # Backward pass: compute gradient of the loss with respect to model parameters
            optimizer.step()  # Perform a single optimization step (parameter update)

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        epoch_loss = running_loss / total
        epoch_acc = correct / total

        # Validation phase
        model.eval()  # Set model to evaluate mode
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for val_images, val_labels in validation_loader:
                val_images, val_labels = val_images.to(device), val_labels.to(
                    device)  # Move validation data to the device
                val_outputs = model(val_images)
                val_loss += criterion(val_outputs, val_labels).item() * val_images.size(0)
                _, val_predicted = torch.max(val_outputs, 1)
                val_total += val_labels.size(0)
                val_correct += (val_predicted == val_labels).sum().item()

        val_epoch_loss = val_loss / val_total
        val_epoch_acc = val_correct / val_total

        print(
            f'Epoch {epoch + 1}: Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f} | Validation Loss: {val_epoch_loss:.4f} Acc: {val_epoch_acc:.4f}')

    print('Training complete')
    return model


def test_model(model, test_loader, device):
    """Test the model using the test data loader and return the test accuracy"""

    model.eval()  # Set the model to evaluation mode
    total = 0
    correct = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            # Print predictions and actual labels
            for p, a in zip(predicted, labels):
                print(f"Predicted: {p.item()}, Actual: {a.item()}")

    test_acc = correct / total
    print(f'Test Accuracy: {test_acc:.4f}')
    return test_acc


def save_model(model, identifier=''):
    """Save the model to a file"""

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'mallampati_models/CNN models/model_{identifier}_{timestamp}.pth'
    torch.save(model.state_dict(), filename)
    print(f'Model saved as {filename}')


if __name__ == '__main__':
    # Create the layers for the CNN
    layers = create_layers()

    # Initialize model, optimizer, and loss function
    model, optimizer, criterion = initialize_model(layers)

    # Load data using DataLoader
    train_loader, validation_loader, test_loader = prepare_image_data(display_images=False, path='mallampati_datasets/mallampati_training_data (2 classes)')

    # Use the following line if you want to use only training and validation data
    # train_loader, validation_loader = prepare_training_and_validation_data(display_images=False, path='mallampati_datasets/New Data')

    # Check for GPU else use CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # Train the model
    trained_model = train_model(model, train_loader, validation_loader, criterion, optimizer, device, num_epochs=10)

    # Test the model
    test_accuracy = test_model(trained_model, test_loader, device)

    # Save the model
    save_model(trained_model, 'mallampati_CNN')
