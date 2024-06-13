import copy
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from mallampati_image_prep import prepare_loader
from functions import imshow_cv
import matplotlib.pyplot as plt

# Hyperparameters
num_classes = 2  # The number of classes in the dataset
learning_rate = 0.00001  # The learning rate for the optimizer
num_epochs = 8  # The number of epochs to train the model
#batch_size = 16  # The batch size for the dataloaders
weight_decay = 0.001  # The weight decay for the optimizer
optimizer_type = 'adam'  # The type of optimizer to use ('adam' or 'sgd')


def run_mallampati_model():
    train_loader = prepare_loader(path='mallampati_datasets/training_data(ManualSplit)')
    validation_loader = prepare_loader(path='mallampati_datasets/validation_data(ManualSplit)')

    # Load the pre-trained VGG19 model
    model = models.vgg19(weights='VGG19_Weights.DEFAULT')
    # Freeze the parameters for all layers
    for param in model.parameters():
        param.requires_grad = False
    # Replace the classifier with a new classifier
    num_features = model.classifier[0].in_features
    model.classifier = nn.Sequential(
        nn.Linear(num_features, 4096),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(4096, 4096),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(4096, num_classes)
    )

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    criterion = nn.CrossEntropyLoss()

    # Choose the optimizer
    if optimizer_type.lower() == 'adam':
        optimizer = optim.Adam(model.classifier.parameters(), lr=learning_rate, weight_decay=weight_decay)
    elif optimizer_type.lower() == 'sgd':
        optimizer = optim.SGD(model.classifier.parameters(), lr=learning_rate, weight_decay=weight_decay, momentum=0.9)
    else:
        raise ValueError(f"Unsupported optimizer type: {optimizer_type}")

    best_model_wts = copy.deepcopy(model.state_dict())
    best_validation_loss = float('inf')
    best_validation_epoch = 0

    training_losses = []
    validation_losses = []
    accuracies = []

    # Training loop
    for epoch in range(num_epochs):
        model.train()  # Set model to training mode
        running_loss = 0.0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
        training_loss = running_loss / len(train_loader.dataset)
        training_losses.append(training_loss)

        # Validation phase
        model.eval()  # Set model to evaluate mode
        validation_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, labels in validation_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                validation_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                correct += torch.sum(preds == labels.data)
                total += labels.size(0)
        validation_loss /= len(validation_loader.dataset)
        validation_losses.append(validation_loss)

        epoch_acc = correct.double() / total
        accuracies.append(epoch_acc.item())

        print(
            f'Epoch {epoch + 1}/{num_epochs}, Training Loss: {training_loss:.4f} | '
            f'Validation Loss: {validation_loss:.4f}, Validation Accuracy: {epoch_acc:.4f}')

        # Saves the model with the best validation loss
        if validation_loss < best_validation_loss:
            best_validation_loss = validation_loss
            best_validation_epoch = epoch
            best_model_wts = copy.deepcopy(model.state_dict())

    model.load_state_dict(best_model_wts)
    folder_name = f'mallampati_models/VGG19_models/loss_{best_validation_loss:.4f}_{num_epochs}_epochs'
    os.makedirs(folder_name, exist_ok=True)

    print(f"Model and training details saved in folder: {folder_name}")
    print(f"Best Validation Loss: {best_validation_loss:.4f} at epoch: {best_validation_epoch + 1}")

    # Save the model
    torch.save(model.state_dict(), os.path.join(folder_name, 'model.pth'))

    # Save hyperparameters
    with open(os.path.join(folder_name, 'hyperparameters.txt'), 'w') as f:
        f.write(f'Num Classes: {num_classes}\n')
        f.write(f'Learning Rate: {learning_rate}\n')
        f.write(f'Num Epochs: {num_epochs}\n')
        f.write(f'Weight Decay: {weight_decay}\n')
        f.write(f'Optimizer Type: {optimizer_type}\n')
        f.write(f'Best Validation Loss: {best_validation_loss:.4f} at epoch: {best_validation_epoch + 1}\n')

    # Save the plot
    plot_file_path = os.path.join(folder_name, 'training_validation_plot.png')
    plot_training(training_losses, validation_losses, accuracies, plot_file_path)


def plot_training(training_losses, validation_losses, accuracies, plot_file_path):
    epochs = range(1, len(training_losses) + 1)
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, training_losses, 'bo-', label='Training Loss')
    plt.plot(epochs, validation_losses, 'ro-', label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(epochs, accuracies, 'go-', label='Validation Accuracy')
    plt.title('Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.tight_layout()
    plt.savefig(plot_file_path)
    plt.close()


if __name__ == "__main__":
    run_mallampati_model()
