import torch
import torch.nn as nn
import numpy as np
from scipy.spatial.distance import mahalanobis, euclidean

from library import mallampati_ResNet_run_model
from library.mallampati_image_prep import prepare_loader
from library.mallampati_CNN_run_model import load_model_CNN
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Define the Feature Extractor
class FeatureExtractor(nn.Module):
    def __init__(self, base_model):
        super(FeatureExtractor, self).__init__()
        self.features = nn.Sequential(*list(base_model.children())[:-1])

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        return x

# Feature extraction function
def extract_features(dataloader, model, device):
    model.to(device)
    model.eval()
    features = []
    labels = torch.Tensor().to(device)
    with torch.no_grad():
        for images, labels_batch in dataloader:
            images = images.to(device)
            feature = model(images)
            features.append(feature)
            labels = torch.cat((labels, labels_batch.to(device)))
    features = torch.cat(features)
    return features, labels

# Mahalanobis Distance Classifier
def mahalanobis_classifier(features, labels, regularization=1e-5):
    # Extract features for each class
    class0_features = features[labels == 0].numpy()
    class1_features = features[labels == 1].numpy()

    # Calculate the mean of each class
    mean0 = np.mean(class0_features, axis=0)
    mean1 = np.mean(class1_features, axis=0)

    # Calculate the covariance matrix for each class and regularize
    cov0 = np.cov(class0_features, rowvar=False) + np.eye(class0_features.shape[1]) * regularization
    cov1 = np.cov(class1_features, rowvar=False) + np.eye(class1_features.shape[1]) * regularization

    # Invert the covariance matrices
    cov0_inv = np.linalg.inv(cov0)
    cov1_inv = np.linalg.inv(cov1)

    # Classifier function
    def classify(x):
        dist0 = mahalanobis(x, mean0, cov0_inv)
        dist1 = mahalanobis(x, mean1, cov1_inv)
        return 0 if dist0 < dist1 else 1

    return classify

# Euclidean Distance Classifier
def euclidean_classifier(features, labels):
    class0_features = features[labels == 0].numpy()
    class1_features = features[labels == 1].numpy()
    mean0 = np.mean(class0_features, axis=0)
    mean1 = np.mean(class1_features, axis=0)
    return lambda x: 0 if euclidean(x, mean0) < euclidean(x, mean1) else 1

# Plot features using PCA
def plot_features(features, labels, title='Feature Plot'):
    pca = PCA(n_components=2)
    reduced_features = pca.fit_transform(features.numpy())
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(reduced_features[:, 0], reduced_features[:, 1], c=labels.numpy(), cmap='viridis', alpha=0.5)
    plt.title(title)
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.colorbar(scatter, label='Class Labels')
    plt.show()

# Main function
def main():
    device = torch.device("cpu")
    train_loader = prepare_loader('mallampati_datasets/training_data', image_pixel_size=64)
    test_loader = prepare_loader('mallampati_datasets/test_data', image_pixel_size=64)

    # Loading original model for normal classification
    full_model = load_model_CNN(device, model_path='mallampati_models/CNN Models/model_mallampati_CNN_20240506_102522.pth')
    feature_extractor_model = FeatureExtractor(full_model)

    train_features, train_labels = extract_features(train_loader, feature_extractor_model, device)
    test_features, test_labels = extract_features(test_loader, feature_extractor_model, device)

    plot_features(train_features, train_labels, title='Train Feature Space')
    plot_features(test_features, test_labels, title='Test Feature Space')

    # Mahalanobis classifier
    m_classifier = mahalanobis_classifier(train_features, train_labels)
    m_predictions = [m_classifier(f.numpy()) for f in test_features]
    m_accuracy = np.mean(np.array(m_predictions) == test_labels.numpy())
    print(f"Mahalanobis Classifier Accuracy: {m_accuracy * 100:.2f}%")

    # Euclidean classifier
    e_classifier = euclidean_classifier(train_features, train_labels)
    e_predictions = [e_classifier(f.numpy()) for f in test_features]
    e_accuracy = np.mean(np.array(e_predictions) == test_labels.numpy())
    print(f"Euclidean Classifier Accuracy: {e_accuracy * 100:.2f}%")

    # Neural Network Normal Classification
    full_model.to(device)
    full_model.eval()
    nn_predictions = []
    with torch.no_grad():
        for images, _ in test_loader:
            images = images.to(device)
            outputs = full_model(images)
            predicted_classes = outputs.max(1)[1]
            nn_predictions.extend(predicted_classes.cpu().numpy())
    nn_accuracy = np.mean(np.array(nn_predictions) == test_labels.numpy())
    print(f"Neural Network Classifier Accuracy: {nn_accuracy * 100:.2f}%")

if __name__ == '__main__':
    main()
