import datetime
import torch
import torch.nn as nn
import torch.optim as optim
from library.mallampati_image_prep import prepare_loader


def initialize_model():
    """Function to initialize the model, optimizer, and loss function for training"""

    model = nn.Sequential(
        nn.Conv2d(3, 32, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        nn.Conv2d(32, 64, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        nn.Conv2d(64, 128, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        nn.Flatten(),
        nn.Linear(128 * 8 * 8, 512),
        nn.ReLU(),
        nn.Linear(512, 2)
    )
    optimizer = optim.Adam(model.parameters(), lr=0.001)  # Using Adam optimizer
    criterion = nn.CrossEntropyLoss()  # Cross-entropy loss
    return model, optimizer, criterion


def find_device():
    """Find the device to run the model on"""

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    return device


def train_model(model, train_loader, validation_loader, criterion, optimizer, device, num_epochs=15):
    """Train the model using the training and validation data loaders for a specified number of epochs"""

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


def save_model(model):
    """Save the model to a file"""

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'mallampati_models/CNN models/model_mallampati_CNN_{timestamp}.pth'
    torch.save(model.state_dict(), filename)
    print(f'Model saved as {filename}')


if __name__ == '__main__':
    # Initialize model, optimizer, and loss function
    model, optimizer, criterion = initialize_model()

    # Random split training and validation data
    # train_loader, validation_loader = prepare_training_and_validation_loaders(image_pixel_size=64, display_images=False, path='mallampati_datasets/New Data')

    # Manual split training and validation data
    train_loader = prepare_loader(path='mallampati_datasets/training_data(ManualSplit)', image_pixel_size=64)
    validation_loader = prepare_loader(path='mallampati_datasets/validation_data(ManualSplit)', image_pixel_size=64)

    # Find the device to run the model on (GPU or CPU)
    device = find_device()

    # Train the model
    trained_model = train_model(model, train_loader, validation_loader, criterion, optimizer, device, num_epochs=15)

    # Save the model
    save_model(trained_model)
