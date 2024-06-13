import torch
from library.mallampati_CNN_train_model import initialize_model, find_device, test_model
from library.mallampati_image_prep import prepare_loader


def load_model_CNN(device, model_path='mallampati_models/model_mallampati_CNN_Best_Model_CUDA.pth'):
    """Load the pre-trained model and run predictions on the test set"""

    # Initialize the model
    model, optimizer, criterion = initialize_model()

    # Load the pre-trained model
    model.load_state_dict(torch.load(model_path, map_location=device))

    model.to(device)

    return model


def run_predictions_on_image(model, image, device):
    """Run predictions on a single image from the pipeline and return the predicted class"""

    model.eval()  # Set the model to evaluation mode

    with torch.no_grad():
        image = image.to(device)
        output = model(image)
        _, predicted = torch.max(output.data, 1)

    return predicted.item()


if __name__ == '__main__':
    # Find the device
    device = find_device()

    # Load the model and move to device
    model = load_model_CNN(device, model_path='mallampati_models/CNN models/model_mallampati_CNN_20240601_160726_82%_test_data.pth')

<<<<<<< Updated upstream
    # Prepare the test loader
    test_loader = prepare_loader(path='mallampati_datasets/test_data', image_pixel_size=64)
    test_loader_discarded = prepare_loader(path='mallampati_datasets/test_data(discarded)', image_pixel_size=64)
=======
    # Parameters
    test_folder_path = 'mallampati_datasets/test_data(ManualSplit)'
    output_file_path = 'predictions.txt'
    image_size = 64  # Assuming the image size used in training
>>>>>>> Stashed changes

    # Test the model on the test data
    test_model(model, test_loader, device)
    test_model(model, test_loader_discarded, device)
