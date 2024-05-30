from PIL import Image
from datetime import datetime, timedelta
import math
from picamera import PiCamera
from time import sleep
from pathlib import Path
import os

def capture_images(image_path, max_storage_size=250, max_images=42, max_capture_duration=480, capture_interval=5):
    """
    Capture images until the maximum storage size or maximum number of images is reached.

    Parameters:
    - image_path: The directory path where images will be saved.
    - max_storage_size: Maximum storage size in MB. Default is 250 MB.
    - max_images: Maximum number of images to capture. Default is 42.
    - max_capture_duration: Maximum capture duration in seconds. Default is 480 seconds.
    - capture_interval: Time interval between captures in seconds. Default is 5 seconds.

    Returns:
    - images: List of captured image file paths.
    - timestamps: List of corresponding capture timestamps.
    """
    try:
        # Sets parameters for PiCamera
        camera = PiCamera()
        camera.resolution = (2592, 1944)
        camera.framerate = 15
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'

        # Creates list for image file paths and corresponding capture timestamps as well as starting the timer
        images = []
        timestamps = []
        total_storage_size = 0
        start_time = datetime.now()

        while total_storage_size < max_storage_size and len(images) < max_images:
            # Records the timestamp when the image was taken and creates a path and name
            timestamp = datetime.now()
            image_name = f"image_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
            image_file = f"{image_path}/{image_name}"

            # Captures the image
            camera.capture(image_file)
            print(f"Image captured: {image_name}")

            # Adds the new image file path and timestamp to the existing lists
            images.append(image_file)
            timestamps.append(timestamp)

            # Calculate total storage size
            total_storage_size += os.path.getsize(image_file) / (1024 * 1024)  # Convert to MB

            # Check if max_capture_duration is reached
            if (timestamp - start_time).total_seconds() > max_capture_duration:
                break

            sleep(capture_interval)

        return images, timestamps

    except Exception as e:
        print(f"Error: {e}")
        return None, None

    finally:
        camera.close()


def extract_coordinates_and_timestamp(image_path):
    """
    Extract GPS coordinates and timestamp from an image using its Exif data.

    Parameters:
    - image_path: Path to the image file.

    Returns:
    - latitude: Latitude in decimal degrees.
    - longitude: Longitude in decimal degrees.
    - timestamp: Timestamp as a datetime object.
    """
    try:
        # Open the image file
        img = Image.open(image_path)

        # Extract GPS Info from Exif data
        exif_data = img._getexif()

        # Check if GPSInfo and DateTimeOriginal exist in the Exif data
        if 0x8825 in exif_data and 0x9003 in exif_data:
            gps_info = exif_data[0x8825]

            # Extract latitude and longitude
            latitude = gps_info[2][0] + gps_info[2][1] / 60 + gps_info[2][2] / 3600
            longitude = gps_info[4][0] + gps_info[4][1] / 60 + gps_info[4][2] / 3600

            # Check the hemisphere (N/S, E/W)
            if gps_info[3] == 'S':
                latitude = -latitude
            if gps_info[1] == 'W':
                longitude = -longitude

            # Extract timestamp and convert it to datetime
            timestamp_str = exif_data[0x9003]
            timestamp = datetime.strptime(timestamp_str, '%Y:%m:%d %H:%M:%S')

            return latitude, longitude, timestamp

        else:
            print("No GPS information or DateTimeOriginal found in the image.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate haversine distance between two sets of latitude and longitude coordinates.

    Parameters:
    - lat1, lon1: Latitude and longitude of the first point in decimal degrees.
    - lat2, lon2: Latitude and longitude of the second point in decimal degrees.

    Returns:
    - distance: Haversine distance between the two points in kilometers.
    """
    radius_of_earth = 6378.137
    mean_distance_from_iss_earth = 400
    # Earth's radius in kilometers added to the mean distance of the ISS from the Earth
    radius_from_centre_of_earth_to_iss = radius_of_earth + mean_distance_from_iss_earth

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Calculate differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate distance
    distance = radius_from_centre_of_earth_to_iss * c
    return distance


def calculate_speed(distance, time_difference):
    """
    Calculate speed given the distance between two points and the time difference.

    Parameters:
    - distance: Distance between two points in kilometers.
    - time_difference: Time difference between two points as a timedelta object.

    Returns:
    - speed: Speed in kilometers per second (always positive).
    """
    # Convert time difference to seconds
    time_in_seconds = time_difference.total_seconds()

    # Calculate speed in kilometers per second
    speed = distance / time_in_seconds
    return abs(speed)  # Always positive


def log_average_speed_to_txt(avg_speed, txt_file):
    """
    Log the average speed to a text file.

    Parameters:
    - avg_speed: Average speed in kilometers per second.
    - txt_file: Path to the text file.
    """
    with open(txt_file, 'w') as file:
        file.write(f"{avg_speed:.2f} km/s\n")


def main():
    # Declares the path to save images as well as where to save the 'result.txt'
    base_folder = Path(__file__).parent.resolve()
    image_save_path = base_folder
    txt_file = base_folder / "result.txt"

    images, timestamps = capture_images(image_save_path)

    if images and timestamps:
        speed_data = []

        for i in range(1, len(images)):
            # Cycles through the images in pairs
            data1 = extract_coordinates_and_timestamp(images[i - 1])
            data2 = extract_coordinates_and_timestamp(images[i])

            if data1 and data2:
                latitude1, longitude1, timestamp1 = data1
                latitude2, longitude2, timestamp2 = data2

                # Check if the images are the same or have zero distance or time
                if images[i - 1] == images[i] or haversine_distance(latitude1, longitude1, latitude2,
                                                                    longitude2) == 0 or (
                        timestamp2 - timestamp1).total_seconds() == 0:
                    continue

                # Calculate distance between the two points
                distance = haversine_distance(latitude1, longitude1, latitude2, longitude2)

                # Calculate time difference
                time_difference = timestamp2 - timestamp1

                # Calculate speed
                speed = calculate_speed(distance, time_difference)

                # Log data
                entry = [images[i - 1], images[i], distance, time_difference.total_seconds(), speed]
                speed_data.append(entry)

        # Calculate average speed
        avg_speed = sum(entry[4] for entry in speed_data) / len(speed_data)

        #Adjusting for the 0.5% error in haversine geographical calculation due to variance in the earth's radius and the ISS's orbit height
        haversine_error_correction_percentage = 0.05
        error_corrected_average_speed = avg_speed * (1+haversine_error_correction_percentage)

        print(f"Average Speed: {error_corrected_average_speed:.3f} km/s")

        # Log average speed to TXT file
        log_average_speed_to_txt(error_corrected_average_speed, txt_file)

        # Delete images to leave only 42
        while len(images) > 42:
            os.remove(images.pop(0))


if __name__ == "__main__":
    main()
