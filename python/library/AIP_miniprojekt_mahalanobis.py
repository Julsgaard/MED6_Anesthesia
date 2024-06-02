import torch
import torch.nn as nn
import numpy as np
from torchvision import transforms
from scipy.spatial.distance import mahalanobis
from library.mallampati_image_prep import prepare_loader
from library.mallampati_CNN_run_model import load_model_CNN, run_predictions_on_image


# Define the Feature Extractor
class FeatureExtractor(nn.Module):
    def __init__(self, base_model):
        super(FeatureExtractor, self).__init__()
        # Load a pre-trained ResNet and remove its final fully connected layer
        self.features = nn.Sequential(*list(base_model.children())[:-1])

    def forward(self, x):
        x = self.features(x)  # Extract features
        x = torch.flatten(x, 1)  # Flatten the features
        return x


# Data loader
# def load_data(data_dir, batch_size):
#     transform = transforms.Compose([
#         transforms.Resize((64, 64)),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#     ])
#     dataset = datasets.ImageFolder(root=data_dir, transform=transform)
#     dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
#     return dataloader

# Feature extraction
def extract_features(dataloader, model, device):
    model.to(device)  # Move the model to the GPU if available
    model.eval()
    features = []
    labels = torch.Tensor().to(device)  # Initialize labels as an empty tensor on the device
    with torch.no_grad():
        for images, labels_batch in dataloader:
            images = images.to(device)
            labels = torch.tensor(labels).to(device)
            feature = model(images)
            features.append(feature)
            labels = torch.cat((labels, labels_batch))
    features = torch.cat(features)
    return features, labels

# Mahalanobis Distance Classifier
def mahalanobis_classifier(features, labels, regularization=1e-5):
    class0_features = features[labels == 0].numpy()
    class1_features = features[labels == 1].numpy()
    mean0 = np.mean(class0_features, axis=0)
    mean1 = np.mean(class1_features, axis=0)
    cov_class0 = np.cov(class0_features.T)
    cov_class1 = np.cov(class1_features.T)
    reg_cov_class0 = cov_class0 + np.eye(cov_class0.shape[0]) * regularization
    cov_inv_class0 = np.linalg.inv(reg_cov_class0)
    reg_cov_class1 = cov_class1 + np.eye(cov_class1.shape[0]) * regularization
    cov_inv_class1 = np.linalg.inv(reg_cov_class1)

    def classify(x):
        dist0 = mahalanobis(x, mean0, cov_inv_class0)
        dist1 = mahalanobis(x, mean1, cov_inv_class1)
        return 0 if dist0 < dist1 else 1

    return classify


def test_model_CNN(dataloader, model):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in dataloader:
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    accuracy = 100 * correct / total
    return accuracy
# Main function
def main():
    # layers_config = [
    #     {'type': 'conv', 'out_channels': 16, 'kernel_size': 3, 'padding': 1},
    #     {'type': 'relu'},
    #     {'type': 'pool', 'kernel_size': 2, 'stride': 2},
    #     {'type': 'conv', 'out_channels': 32, 'kernel_size': 3, 'padding': 1},
    #     {'type': 'relu'},
    #     {'type': 'pool', 'kernel_size': 2, 'stride': 2}
    # ]

    # Convolutional Layer: Extracts a wide array of features from the input image through convolution.

    # ReLU Layer: Applies non-linearity, making the model capable of learning complex patterns.
    # Without ReLU, the network would be computing linear operations, thus less capable of grasping complex structures in the data.
    # Often used after convolution layer

    # Pooling Layer: Reduces the spatial dimensions of the output from the previous layers,
    # summarizing the features extracted thus far, and reducing the sensitivity of the output to the exact location of features in the input.
    # Often used after ReLU layer

    # Load and extract features
    train_loader = prepare_loader(path='mallampati_datasets/training_data(ManualSplit)', image_pixel_size=64)
    test_loader = prepare_loader(path='mallampati_datasets/test_data(ManualSplit)', image_pixel_size=64)
    # If you want to use the model that is created inside this script, use this code:
    #train_features, train_labels = extract_features(train_loader, FeatureExtractor(layers_config))
    #test_features, test_labels = extract_features(test_loader, FeatureExtractor(layers_config))

    # Set device to CPU
    device = torch.device("cpu")

    # If you want to use a pretrained model, use this code:

    feature_extractor_model = FeatureExtractor(load_model_CNN(device, 'mallampati_models/model_mallampati_CNN_Best.pth'))
    train_features, train_labels = extract_features(train_loader, feature_extractor_model, device)
    test_features, test_labels = extract_features(test_loader, feature_extractor_model, device)
    normal_model = load_model_CNN(device, 'mallampati_models/model_mallampati_CNN_Best.pth')
    # Train and apply classifier
    classifier = mahalanobis_classifier(train_features, train_labels, regularization=1e-5)
    predictions = [classifier(f.numpy()) for f in test_features]
    accuracy = np.mean(np.array(predictions) == test_labels.numpy())
    print(f"Accuracy on test Mahalanobis: {accuracy * 100:.2f}%")
    CNNAccuracy = test_model_CNN(test_loader,normal_model)
    print(f"Accuracy on test CNN: {CNNAccuracy:.2f}%")



    # After extracting features
    #np.save('AIP_Feature_Data/train_features.npy', train_features.numpy())
    #np.save('AIP_Feature_Data/train_labels.npy', train_labels.numpy())
    #np.save('AIP_Feature_Data/test_features.npy', test_features.numpy())
    #np.save('AIP_Feature_Data/test_labels.npy', test_labels.numpy())

if __name__ == '__main__':
    main()
