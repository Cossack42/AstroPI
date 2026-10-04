# AstroPI - NCS_Orbit

Team NCS Orbit's entry for the European Space Agency's Astro Pi Mission Space Lab challenge, developed between November 2023 and February 2024. Our program ran aboard the International Space Station in 2024, where it captured images with the onboard camera, read the GPS coordinates and timestamps from the image metadata, and used the haversine formula to calculate the station's orbital speed.

**Result: the program measured the ISS's orbital speed as 7.75 km/s against an actual speed of 7.66 km/s — a percentage error of roughly 1.2%.**

This repository contains two main components: the submitted code for the competition, `main.py`, and the resources and past iterations of the code, along with an exemplar script using image matching, in the folder `astropi-iss-speed-en-resources`.

## How the code works

The code is designed to capture images using a Raspberry Pi camera, extract GPS coordinates and timestamps from the images, calculate the speed of the ISS (since the camera is on the ISS), and log the average speed to a text file. Here's a detailed explanation:

### Imports

- **`from PIL import Image`**: Used for image processing.
- **`from datetime import datetime, timedelta`**: For handling dates and times.
- **`import math`**: Provides mathematical functions.
- **`from picamera import PiCamera`**: Used to control the Raspberry Pi Camera.
- **`from time import sleep`**: For adding delays between operations.
- **`from pathlib import Path`**: For handling file system paths.
- **`import os`**: For interacting with the operating system, particularly the file system.

### Function Definitions

1. **`capture_images(image_path, max_storage_size=250, max_images=42, max_capture_duration=480, capture_interval=5)`**:
   - Captures images with the PiCamera until one of the limits is reached (storage size, number of images, or capture duration).
   - Parameters:
     - `image_path`: Directory where images are saved.
     - `max_storage_size`: Maximum storage size in MB.
     - `max_images`: Maximum number of images to capture.
     - `max_capture_duration`: Maximum duration for capturing images in seconds.
     - `capture_interval`: Time interval between captures in seconds.
   - Returns lists of captured image file paths and corresponding timestamps.

2. **`extract_coordinates_and_timestamp(image_path)`**:
   - Extracts GPS coordinates and timestamps from the image's EXIF data.
   - Parameters:
     - `image_path`: Path to the image file.
   - Returns latitude, longitude, and timestamp if available, otherwise `None`.

3. **`haversine_distance(lat1, lon1, lat2, lon2)`**:
   - Calculates the haversine distance between two sets of latitude and longitude coordinates.
   - Parameters:
     - `lat1, lon1`: Latitude and longitude of the first point.
     - `lat2, lon2`: Latitude and longitude of the second point.
   - Returns the distance in kilometers.

4. **`calculate_speed(distance, time_difference)`**:
   - Calculates speed given the distance and time difference.
   - Parameters:
     - `distance`: Distance between two points in kilometers.
     - `time_difference`: Time difference between two points as a `timedelta` object.
   - Returns speed in kilometers per second.

5. **`log_average_speed_to_txt(avg_speed, txt_file)`**:
   - Logs the average speed to a text file.
   - Parameters:
     - `avg_speed`: Average speed in kilometers per second.
     - `txt_file`: Path to the text file.

### Main Function

- **`main()`**:
  - Sets paths for saving images and the result text file.
  - Calls `capture_images` to capture images and get their timestamps.
  - Extracts coordinates and timestamps from each pair of images.
  - Calculates the distance and speed between consecutive images.
  - Computes the average speed, applies an error correction, and logs it to the text file.
  - Deletes images if there are more than 42.

### Execution

- **`if __name__ == "__main__": main()`**: Ensures the `main` function is called when the script is executed directly.

### Usage

1. **Capturing Images**:
   - The `capture_images` function initialises the camera, captures images at specified intervals, and stores them in the specified directory.

2. **Extracting Data**:
   - The `extract_coordinates_and_timestamp` function reads each image's EXIF data to get GPS coordinates and the timestamp.

3. **Calculating Distances and Speed**:
   - The `haversine_distance` function calculates the distance between consecutive GPS coordinates.
   - The `calculate_speed` function computes the speed based on the distance and the time difference between captures.

4. **Logging Average Speed**:
   - The `log_average_speed_to_txt` function writes the calculated average speed to a text file.

5. **Maintaining Image Count**:
   - The script ensures that no more than 42 images are stored by deleting the oldest ones if necessary, to stay within the 250 MB storage limit.
