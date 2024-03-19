# This script is a variant of the HeadAngle_ImageProcessing script but instead only uses the phone sensor and no image processing.

phone_angle_list = []  # A list to store the phone angles for each picture


def store_and_calculate_absolute_tilt_angle(phone_angle):
    """Calculates how much the neck has been tilted based on a list of phone angles.

        :param phone_angle: The phone angle from the phone sensor.
        :return: The absolute distance between the highest and lowest values and the default tilt angle."""
    phone_angle_list.append(phone_angle)

    absolute_distance = None
    default_tilt_angle = None

    if len(phone_angle_list) >= 20:  # 20 is just for now, we can adjust later when we know exactly how long they should perform the exercise
        # Finding the highest and lowest values
        highest_value = max(phone_angle_list)
        lowest_value = min(phone_angle_list)

        # Calculating the absolute distance between the highest and lowest values
        absolute_distance = abs(highest_value - lowest_value)

        # Calculating the average of the first 5 values -> Will adjust whether it should be the first 5 values later
        default_tilt_angle = sum(phone_angle_list[:5]) / 5

        # Optional: Clear the list after calculations if needed
        phone_angle_list.clear()
        #print(f"Absolute distance: {absolute_distance}")
        #print(f"Max value: {highest_value}")
        #print(f"Min value: {lowest_value}")

        # Returning the absolute distance and default tilt angle
    return absolute_distance, default_tilt_angle


if __name__ == "__main__":
    print("Not meant to be run directly")
