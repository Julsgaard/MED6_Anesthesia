import numpy as np
from PIL import Image
import torch
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader, random_split
from library.functions import imshow_cv


def prepare_training_validation_and_test_loaders(image_pixel_size=224,
                                                 path='mallampati_datasets/mallampati_training_data (2 classes)',
                                                 display_images=False):
    transform = prepare_transform(image_pixel_size)

    # Load the dataset and apply the transformations
    dataset = ImageFolder(root=path, transform=transform)

    # Splitting the dataset into train, validation, and test sets
    train_size = int(0.7 * len(dataset))  # 70% for training
    validation_size = int(0.15 * len(dataset))  # 15% for validation
    test_size = len(dataset) - (train_size + validation_size)  # Remaining ~15% for testing

    # Vi får den til at splitte det randomly lige nu, men kan godt være vi selv skal gøre det og gemme det? Eller får den til det
    train_dataset, validation_dataset, test_dataset = random_split(dataset, [train_size, validation_size, test_size])

    # Creating data loaders for training, validation, and testing
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    validation_loader = DataLoader(validation_dataset, batch_size=4, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False)

    print(f"Number of training samples: {len(train_dataset)}")
    print(f"Number of validation samples: {len(validation_dataset)}")
    print(f"Number of testing samples: {len(test_dataset)}")

    if display_images:  # Display a few images
        for i, (inputs, labels) in enumerate(train_loader):
            if i == 10:  # Display first 10 images
                break
            imshow_cv(inputs[0])  # Display the first image from the batch

    return train_loader, validation_loader, test_loader


def prepare_training_and_validation_loaders(image_pixel_size=224,
                                            path='mallampati_datasets/mallampati_training_data (2 classes)',
                                            display_images=False):
    transform = transforms.Compose([
        transforms.Resize(image_pixel_size),
        transforms.CenterCrop(image_pixel_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Load the dataset and apply the transformations
    dataset = ImageFolder(root=path, transform=transform)

    # Splitting the dataset into train and validation sets
    train_size = int(0.85 * len(dataset))  # 85% for training
    validation_size = len(dataset) - train_size  # Remaining for validation

    train_dataset, validation_dataset = random_split(dataset, [train_size, validation_size])

    # Creating data loaders for training, validation, and testing
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    validation_loader = DataLoader(validation_dataset, batch_size=4, shuffle=False)

    print(f"Number of training samples: {len(train_dataset)}")
    print(f"Number of validation samples: {len(validation_dataset)}")

    if display_images:
        # Example code to display images from each dataset
        for i, (inputs, labels) in enumerate(train_loader):
            if i == 10:  # Display first 10 images
                break
            imshow_cv(inputs[0])  # Display the first image from the batch

    return train_loader, validation_loader


def prepare_augmented_image_data(image_pixel_size=224,
                                 path='mallampati_datasets/mallampati_training_data (2 classes)'):  # TODO: Try this

    # Augmented transformations for training
    train_transform_augmented = transforms.Compose([
        transforms.Resize(image_pixel_size),
        transforms.CenterCrop(image_pixel_size),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Standard transformations for testing (no augmentation)
    test_transform = transforms.Compose([
        transforms.Resize(image_pixel_size),
        transforms.CenterCrop(image_pixel_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Assuming the same dataset for simplicity, use different paths if you have separate datasets
    full_dataset = ImageFolder(root=path)

    # Splitting the dataset
    train_size = int(0.8 * len(full_dataset))
    test_size = len(full_dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(full_dataset, [train_size, test_size])

    # Manually apply transformations by wrapping the dataset subsets
    train_dataset = ImageFolder(root=path, transform=train_transform_augmented)
    test_dataset = ImageFolder(root=path, transform=test_transform)

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


def prepare_test_loader(image_pixel_size=224, path='mallampati_testset/Second testset'):
    # Define transformations
    transform = transforms.Compose([
        transforms.Resize(image_pixel_size),  # Resize the shorter side to 224
        transforms.CenterCrop(image_pixel_size),  # Crop the longer side to 224
        transforms.ToTensor(),  # Convert the image to a PyTorch tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize
    ])

    # Load the dataset and apply the transformations
    dataset = ImageFolder(root=path, transform=transform)

    # Creating data loader for testing
    test_loader = DataLoader(dataset, batch_size=4, shuffle=False)

    print(f"Number of testing samples: {len(dataset)}")

    return test_loader


def prepare_mallampati_image_for_loader(image, image_pixel_size=224):
    # Check if the image is a NumPy array and convert it to PIL Image
    if isinstance(image, np.ndarray):
        # Convert numpy array to PIL Image
        image = Image.fromarray(image)

    transform = transforms.Compose([
        transforms.Resize(image_pixel_size),
        transforms.CenterCrop(image_pixel_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return transform(image)

def prepare_data_loader(path, image_pixel_size, batch_size, shuffle, transform):
    dataset = ImageFolder(root=path, transform=transform)
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
    return data_loader

def prepare_transform(image_pixel_size=224):
    return transforms.Compose([
        transforms.Resize(image_pixel_size),
        transforms.CenterCrop(image_pixel_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

def prepare_training_loader(training_path, image_pixel_size=224, display_images=False):
    'Prepare training data loader when the training data already is manually split (So just provide the folder)'
    transform = prepare_transform(image_pixel_size)
    train_loader = prepare_data_loader(training_path, image_pixel_size, batch_size=4, shuffle=True, transform=transform)

    if display_images:
        for i, (inputs, labels) in enumerate(train_loader):
            if i == 10:
                break
            imshow_cv(inputs[0])

    return train_loader

def prepare_validation_loader(validation_path, image_pixel_size=224):
    'Prepare the validation data when the data already is manually split (So just provide the folder)'
    transform = prepare_transform(image_pixel_size)
    validation_loader = prepare_data_loader(validation_path, image_pixel_size, batch_size=4, shuffle=False, transform=transform)
    return validation_loader


if __name__ == "__main__":
    prepare_training_validation_and_test_loaders()
    # prepare_augmented_image_data()
