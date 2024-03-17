import torch
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from library.functions import imshow_cv


def prepare_image_data():
    # Define your dataset path
    dataset_path = 'mallampati_dataset'

    # # Define transformations
    # transform = transforms.Compose([
    #     transforms.Resize((224, 224)),  # Resize the image
    #     transforms.ToTensor(),  # Convert the image to a PyTorch tensor
    #     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize
    # ])

    transform = transforms.Compose([
        transforms.Resize(224),  # Resize the shorter side to 224
        transforms.CenterCrop(224),  # Crop the longer side to 224
        transforms.ToTensor(),  # Convert the image to a PyTorch tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize
    ])

    # Load the dataset and apply the transformations
    dataset = ImageFolder(root=dataset_path, transform=transform)

    # Splitting the dataset into train and test sets
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    # Creating data loaders for training and testing
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False)

    print(f"Number of training samples: {len(train_dataset)}")
    print(f"Number of testing samples: {len(test_dataset)}")

    # # Display a few images from the training dataset
    # for i, (inputs, labels) in enumerate(train_loader):
    #     if i == 5:  # Display first 5 images
    #         break
    #     imshow_cv(inputs[0])  # Display the first image from the batch
    #
    # # Display a few images from the testing dataset
    # for i, (inputs, labels) in enumerate(test_loader):
    #     if i == 5:  # Display first 5 images
    #         break
    #     imshow_cv(inputs[0])  # Display the first image from the batch

    return train_loader, test_loader


def prepare_augmented_image_data():  # TODO: Try this
    dataset_path = 'mallampati_dataset'

    # Augmented transformations for training
    train_transform_augmented = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Standard transformations for testing (no augmentation)
    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Assuming the same dataset for simplicity, use different paths if you have separate datasets
    full_dataset = ImageFolder(root=dataset_path)

    # Splitting the dataset
    train_size = int(0.8 * len(full_dataset))
    test_size = len(full_dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(full_dataset, [train_size, test_size])

    # Manually apply transformations by wrapping the dataset subsets
    train_dataset = ImageFolder(root=dataset_path, transform=train_transform_augmented)
    test_dataset = ImageFolder(root=dataset_path, transform=test_transform)

    # Creating data loaders
    train_loader_augmented = DataLoader(train_dataset, batch_size=4, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False)

    print(f"Number of training samples (augmented): {len(train_dataset)}")
    print(f"Number of testing samples: {len(test_dataset)}")

    # # Display a few images from the training dataset
    # for i, (inputs, labels) in enumerate(train_loader_augmented):
    #     if i == 5:  # Display first 5 images
    #         break
    #     imshow_cv(inputs[0])  # Display the first image from the batch
    #
    # # Display a few images from the testing dataset
    # for i, (inputs, labels) in enumerate(test_loader):
    #     if i == 5:  # Display first 5 images
    #         break
    #     imshow_cv(inputs[0])  # Display the first image from the batch

    return train_loader_augmented, test_loader


def prepare_test_data():
    # Define your test dataset path
    dataset_path = 'mallampati_testset'

    # Define transformations
    transform = transforms.Compose([
        transforms.Resize(224),  # Resize the shorter side to 224
        transforms.CenterCrop(224),  # Crop the longer side to 224
        transforms.ToTensor(),  # Convert the image to a PyTorch tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize
    ])

    # Load the dataset and apply the transformations
    dataset = ImageFolder(root=dataset_path, transform=transform)

    # Creating data loader for testing
    test_loader = DataLoader(dataset, batch_size=4, shuffle=False)

    print(f"Number of testing samples: {len(dataset)}")

    return test_loader


if __name__ == "__main__":
    # prepare_image_data()
    prepare_augmented_image_data()