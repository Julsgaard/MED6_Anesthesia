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
learning_rate = 0.001  # The learning rate for the optimizer
num_epochs = 100  # The number of epochs to train the model


def run_mallampati_model():
    train_loader = prepare_loader(path='mallampati_datasets/training_data(ManualSplit)')
    validation_loader = prepare_loader(path='mallampati_datasets/validation_data(ManualSplit)')

    model = models.resnet34(weights='ResNet34_Weights.DEFAULT')
    for param in model.parameters():
        param.requires_grad = False
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(512, num_classes)
    )

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=learning_rate)

    best_model_wts = copy.deepcopy(model.state_dict())
    best_validation_loss = 0.0

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

        # deep copy the model if it has the best accuracy so far
        if validation_loss > best_validation_loss:
            best_validation_loss = validation_loss
            best_validation_epoch = epoch
            best_model_wts = copy.deepcopy(model.state_dict())

    model.load_state_dict(best_model_wts)
    folder_name = f'mallampati_models/ResNet models/{best_validation_loss:.4f}%_{num_epochs}_epochs'
    os.makedirs(folder_name, exist_ok=True)

    # Save the model
    torch.save(model.state_dict(), os.path.join(folder_name, 'model.pth'))

    # Save hyperparameters
    with open(os.path.join(folder_name, 'hyperparameters.txt'), 'w') as f:
        f.write(f'Num Classes: {num_classes}\n')
        f.write(f'Learning Rate: {learning_rate}\n')
        f.write(f'Num Epochs: {num_epochs}\n')
        f.write(f'Best Validation Loss: {best_validation_loss:.4f}% at epoch: {best_validation_epoch + 1}\n')

    # Save the plot
    plot_file_path = os.path.join(folder_name, 'training_validation_plot.png')
    plot_training(training_losses, validation_losses, accuracies, plot_file_path)

    print(f"Model and training details saved in folder: {folder_name}")
    print(f"Best validation loss: {best_validation_loss * 100:.2f}% at epoch: {best_validation_epoch + 1}")


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
