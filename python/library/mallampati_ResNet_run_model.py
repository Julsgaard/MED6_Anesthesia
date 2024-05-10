import torch
from torch import nn
from torchvision import models
from library.mallampati_image_prep import prepare_loader


def load_model_and_predict():
    num_classes = 2

    # Set the device to GPU if available
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Load the pre-trained model
    model = models.resnet34(weights='ResNet34_Weights.DEFAULT')
    num_features = model.fc.in_features
    print(f"Number of features: {num_features}")
    model.fc = nn.Sequential(
        nn.Linear(num_features, 512),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(512, num_classes)
    )
    model.load_state_dict(torch.load('mallampati_models/ResNet models/97.33%_15_epochs/model.pth'))

    # Move the model to the device
    model.to(device)

    # Set the model to evaluation mode
    model.eval()

    # Gather and prepare the data
    test_loader = prepare_loader(path='mallampati_datasets/test_data(ManualSplit)')

    # Initialize the confusion matrix
    confusion_matrix = torch.zeros(num_classes, num_classes)

    # Initialize a list to hold the total number of images for each class
    total_images_per_class = [0] * num_classes

    # Calculate the total number of images for each class in the test set
    for inputs, labels in test_loader:
        for label in labels:
            total_images_per_class[label.long()] += 1

    # Make predictions on the test set
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)

            # Print the model's prediction and the actual class for each image
            for i in range(len(labels)):
                print(f'Image: Actual class: {labels[i].item()}, Predicted class: {predicted[i].item()}')

            # Update the confusion matrix
            for t, p in zip(labels.view(-1), predicted.view(-1)):
                confusion_matrix[t.long(), p.long()] += 1

        # Calculate and print overall accuracy
        total = torch.sum(confusion_matrix).item()
        correct = torch.trace(confusion_matrix).item()
        overall_acc = correct / total
        print(f'Overall accuracy: {100 * overall_acc} %')

        # Calculate and print accuracy for each class
        for i in range(num_classes):
            class_correct = confusion_matrix[i, i].item()
            class_total = total_images_per_class[i]
            class_acc = class_correct / class_total
            print(f'Class {i + 1} in best epoch: {class_correct} out of {class_total} ({100 * class_acc}%)')


def load_model_ResNet(device, model_path='mallampati_models/ResNet models/model_resnet.pth'):
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


if __name__ == "__main__":
    load_model_and_predict()
