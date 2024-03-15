import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR
from torchvision import models
from library.mallampati_image_prep import prepare_image_data
from library.functions import imshow_cv
import matplotlib.pyplot as plt


# A single measure of accuracy might not tell the whole story. Consider also looking at other metrics like precision, recall, F1 score, and confusion matrices, especially since your dataset is quite small.
# If your model is overfitting, techniques such as adding dropout, regularization, or data augmentation could help. Additionally, ensure you have a validation set to monitor for overfitting during training.
# You might want to implement a learning rate scheduler to adjust the learning rate during training to help the model converge more smoothly.


def run_mallampati_model():
    # Gather and prepare the data
    train_loader, test_loader = prepare_image_data()

    # Load a pre-trained ResNet model and modify it
    model = models.resnet152(weights='ResNet152_Weights.DEFAULT')
    for param in model.parameters():
        param.requires_grad = False  # Freeze parameters to avoid backpropagating through them
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 4)  # Adjust for 4 class output

    # Move the model to GPU if available
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"Device: {device}")  # TODO: Get CUDA to work

    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=0.001)  # Only train the classifier parameters

    # Learning rate scheduler - decay the learning rate by a factor of 0.1 every 7 epochs
    scheduler = StepLR(optimizer, step_size=7, gamma=0.1)

    # Model checkpointing
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    best_epoch = 0
    best_epoch_confusion_matrix = None

    # Initialize the confusion matrix
    num_classes = 4
    confusion_matrix = torch.zeros(num_classes, num_classes)

    # Initialize lists to store losses and accuracies
    losses = []
    accuracies = []

    # Initialize a list to hold the total number of images for each class
    total_images_per_class = [0] * num_classes

    # Calculate the total number of images for each class in the test set
    for inputs, labels in test_loader:
        for label in labels:
            total_images_per_class[label.long()] += 1

    # Training loop
    num_epochs = 5
    for epoch in range(num_epochs):
        confusion_matrix = torch.zeros(num_classes, num_classes)

        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()  # Zero the parameter gradients
            outputs = model(inputs)  # Forward pass
            loss = criterion(outputs, labels)  # Calculate loss
            loss.backward()  # Backward pass
            optimizer.step()  # Optimize

            running_loss += loss.item()
        print(f"Epoch {epoch + 1}, Loss: {running_loss / len(train_loader)}")

        # Append loss for this epoch
        losses.append(running_loss / len(train_loader))

        # Evaluate the model
        model.eval()  # Set the model to evaluation mode
        correct = 0
        total = 0
        epoch_acc = 0
        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

                # Update the confusion matrix
                for t, p in zip(labels.view(-1), predicted.view(-1)):
                    confusion_matrix[t.long(), p.long()] += 1

            epoch_acc = correct / total
            print(f'Accuracy on the test set: {100 * epoch_acc} %')

            # deep copy the model
            if epoch_acc > best_acc:
                best_acc = epoch_acc
                best_epoch = epoch + 1
                best_model_wts = copy.deepcopy(model.state_dict())
                best_epoch_confusion_matrix = confusion_matrix.clone()

        # Append accuracy for this epoch
        accuracies.append(epoch_acc)

        # Step the scheduler
        scheduler.step()
        scheduler.get_last_lr()

    # load best model weights
    model.load_state_dict(best_model_wts)

    print("======================================")
    # Print the best epoch and the number of correct predictions for each class in that epoch
    print(f'Best epoch: {best_epoch}')
    print(f'Test set accuracy in best epoch: {best_acc * 100}%')
    for i in range(num_classes):
        print(f'Class {i + 1} in best epoch: {best_epoch_confusion_matrix[i, i]} out of {total_images_per_class[i]} '
              f'({(best_epoch_confusion_matrix[i, i] / total_images_per_class[i]) * 100}%)')

    # Save the model
    torch.save(model.state_dict(), 'mallampati_models/best_model.pth')

    # Plot the training loss and accuracy
    plot_training(losses, accuracies)


def plot_training(losses, accuracies):
    epochs = range(1, len(losses) + 1)

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, losses, 'bo', label='Training loss')
    plt.title('Training loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(epochs, accuracies, 'bo', label='Training accuracy')
    plt.title('Training accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_mallampati_model()
