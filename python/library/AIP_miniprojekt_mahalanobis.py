import torch
import torch.nn as nn
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
import numpy as np
from scipy.spatial.distance import mahalanobis

# Define the Feature Extractor
class FeatureExtractor(nn.Module):
    def __init__(self, layers_config):
        super(FeatureExtractor, self).__init__()
        self.layers = nn.ModuleList()
        in_channels = 3  # Assuming input images are RGB

        for config in layers_config:
            if config['type'] == 'conv':
                layer = nn.Conv2d(in_channels, config['out_channels'], kernel_size=config['kernel_size'],
                                  padding=config['padding'])
                in_channels = config['out_channels']
            elif config['type'] == 'pool':
                layer = nn.MaxPool2d(kernel_size=config['kernel_size'], stride=config['stride'])
            elif config['type'] == 'relu':
                layer = nn.ReLU()
            self.layers.append(layer)

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        x = x.view(x.size(0), -1)  # Flatten the output for feature vector
        return x

# Data loader
def load_data(data_dir, batch_size):
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    dataset = datasets.ImageFolder(root=data_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    return dataloader

# Feature extraction
def extract_features(dataloader, model):
    model.eval()
    features = []
    labels = []
    with torch.no_grad():
        for images, labels_batch in dataloader:
            feature = model(images)
            features.append(feature)
            labels.extend(labels_batch)
    features = torch.cat(features)
    labels = torch.tensor(labels)
    return features, labels

# Mahalanobis Distance Classifier
def mahalanobis_classifier(features, labels, regularization=1e-5):
    class0_features = features[labels == 0].numpy()
    class1_features = features[labels == 1].numpy()
    mean0 = np.mean(class0_features, axis=0)
    mean1 = np.mean(class1_features, axis=0)
    combined_features = np.vstack([class0_features, class1_features])
    cov = np.cov(combined_features.T)
    reg_cov = cov + np.eye(cov.shape[0]) * regularization
    cov_inv = np.linalg.inv(reg_cov)

    def classify(x):
        dist0 = mahalanobis(x, mean0, cov_inv)
        dist1 = mahalanobis(x, mean1, cov_inv)
        return 0 if dist0 < dist1 else 1

    return classify

# Main function
def main():
    train_dir = 'AIP_Data/TrainingData'
    test_dir = 'AIP_Data/TestData'
    batch_size = 16
    layers_config = [
        {'type': 'conv', 'out_channels': 16, 'kernel_size': 3, 'padding': 1},
        {'type': 'relu'},
        {'type': 'pool', 'kernel_size': 2, 'stride': 2},
        {'type': 'conv', 'out_channels': 32, 'kernel_size': 3, 'padding': 1},
        {'type': 'relu'},
        {'type': 'pool', 'kernel_size': 2, 'stride': 2}
    ]

    # Convolutional Layer: Extracts a wide array of features from the input image through convolution.

    # ReLU Layer: Applies non-linearity, making the model capable of learning complex patterns.
    # Without ReLU, the network would be computing linear operations, thus less capable of grasping complex structures in the data.
    # Often used after convolution layer

    # Pooling Layer: Reduces the spatial dimensions of the output from the previous layers,
    # summarizing the features extracted thus far, and reducing the sensitivity of the output to the exact location of features in the input.
    # Often used after ReLU layer

    # Load and extract features
    train_loader = load_data(train_dir, batch_size)
    test_loader = load_data(test_dir, batch_size)
    train_features, train_labels = extract_features(train_loader, FeatureExtractor(layers_config))
    test_features, test_labels = extract_features(test_loader, FeatureExtractor(layers_config))

    # Train and apply classifier
    classifier = mahalanobis_classifier(train_features, train_labels, regularization=1e-5)
    predictions = [classifier(f.numpy()) for f in test_features]
    accuracy = np.mean(np.array(predictions) == test_labels.numpy())
    print(f"Accuracy on test dataset: {accuracy * 100:.2f}%")

    # After extracting features
    np.save('AIP_Feature_Data/train_features.npy', train_features.numpy())
    np.save('AIP_Feature_Data/train_labels.npy', train_labels.numpy())
    np.save('AIP_Feature_Data/test_features.npy', test_features.numpy())
    np.save('AIP_Feature_Data/test_labels.npy', test_labels.numpy())

if __name__ == '__main__':
    main()
