import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
import datetime
import os



# Data loader
def load_data(data_dir, batch_size):
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    dataset = datasets.ImageFolder(root=data_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    return dataloader


# Model definition
class CustomImageClassifier(nn.Module):
    def __init__(self, layers_config):
        super(CustomImageClassifier, self).__init__()
        self.layers = nn.ModuleList()
        in_channels = 3  # Initial input channels (RGB)

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

        self.temp_x = torch.zeros(1, 3, 64, 64)  # Dummy input
        with torch.no_grad():
            self.temp_x = self.compute_features(self.temp_x)
        flattened_size = int(torch.numel(self.temp_x))
        self.fc = nn.Linear(flattened_size, 2)

    def compute_features(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

    def forward(self, x):
        x = self.compute_features(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


# Validate the model
def validate_model(dataloader, model, criterion):
    model.eval()
    validation_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in dataloader:
            outputs = model(images)
            loss = criterion(outputs, labels)
            validation_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    accuracy = 100 * correct / total
    return validation_loss / len(dataloader), accuracy


# Train the model
def train_model(train_dataloader, val_dataloader, model, criterion, optimizer, num_epochs, save_path):
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_dataloader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        # Validation phase
        val_loss, val_accuracy = validate_model(val_dataloader, model, criterion)
        print(
            f"Epoch {epoch + 1}/{num_epochs}, Loss: {running_loss / len(train_dataloader)}, Validation Loss: {val_loss}, Validation Accuracy: {val_accuracy}%")

    torch.save(model.state_dict(), save_path)
    print(f"Model saved to {save_path}")


# Load the model
def load_model(model_path, layers_config):
    model = CustomImageClassifier(layers_config)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model


# Test the model
def test_model(dataloader, model):
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

def save_configuration(layers_config, hyperparams, save_path, val_accuracy, test_accuracy):
    config_path = save_path.replace('.pth', '_config.txt')
    with open(config_path, 'w') as f:
        f.write("Model Configuration and Hyperparameters:\n\n")
        f.write("Layers:\n")
        for layer in layers_config:
            f.write(f"{layer}\n")
        f.write("\nHyperparameters:\n")
        for key, value in hyperparams.items():
            f.write(f"{key}: {value}\n")
        f.write("\nValidation Accuracy: {:.2f}%\n".format(val_accuracy))
        f.write("Test Accuracy: {:.2f}%\n".format(test_accuracy))
    print(f"Configuration saved to {config_path}")


def create_unique_dir(base_path="AIP_Model"):
    # Create a base directory if it doesn't exist
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # Generate a unique directory name with the current date and time
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_dir = os.path.join(base_path, date_str)
    os.makedirs(unique_dir)
    return unique_dir

# Main function to tie everything together
def main():
    train_dir = 'AIP_Data/TrainingData'
    val_dir = 'AIP_Data/ValidationData'
    test_dir = 'AIP_Data/TestData'
    batch_size = 16
    learning_rate = 0.001
    num_epochs = 20
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

    hyperparams = {
        'batch_size': batch_size,
        'learning_rate': learning_rate,
        'num_epochs': num_epochs
    }

    # Create a unique directory for this run
    save_dir = create_unique_dir()
    model_save_path = os.path.join(save_dir, 'model.pth')

    # Load data
    train_dataloader = load_data(train_dir, batch_size)
    val_dataloader = load_data(val_dir, batch_size)
    test_dataloader = load_data(test_dir, batch_size)

    # Model setup
    model = CustomImageClassifier(layers_config)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Training phase with validation
    train_model(train_dataloader, val_dataloader, model, criterion, optimizer, num_epochs, model_save_path)

    # Validation and testing phase
    _, val_accuracy = validate_model(val_dataloader, model, criterion)
    test_accuracy = test_model(test_dataloader, model)

    # Save model configuration along with accuracy
    save_configuration(layers_config, hyperparams, model_save_path, val_accuracy, test_accuracy)


if __name__ == '__main__':
    main()
