import torch
from torch import nn
from torchvision import models
from library.mallampati_image_prep import prepare_test_data


def load_model_and_predict():
    num_classes = 2

    # Load the pre-trained model
    model = models.resnet34()
    num_features = model.fc.in_features
    print(f"Number of features: {num_features}")
    model.fc = nn.Linear(num_features, num_classes)
    model.load_state_dict(torch.load('mallampati_models/best_model_ResNet34_98%_25_epochs_2_classes.pth'))

    # Move the model to GPU if available
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Set the model to evaluation mode
    model.eval()

    # Gather and prepare the data
    test_loader = prepare_test_data()

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


if __name__ == "__main__":
    load_model_and_predict()
