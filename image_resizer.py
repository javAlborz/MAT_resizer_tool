import cv2
import numpy as np
import os


def find_bounding_box(image):
    """
    Finds the bounding box of the non-white object in the image and dilates it to include shadows.
    Assumes the image has a white background.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return 0, 0, image.shape[1], image.shape[0]

    x_vals = []
    y_vals = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        x_vals.extend([x, x + w])
        y_vals.extend([y, y + h])

    # Determine the minimal bounding box
    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)

    # Dilate the bounding box
    padding = 50  # Adjust this value as needed
    x_min_dilated = max(x_min - padding, 0)
    y_min_dilated = max(y_min - padding, 0)
    x_max_dilated = min(x_max + padding, image.shape[1])
    y_max_dilated = min(y_max + padding, image.shape[0])

    return x_min_dilated, y_min_dilated, x_max_dilated - x_min_dilated, y_max_dilated - y_min_dilated


        
def compute_padding(cropped_shape, template_size):
    """
    Computes the padding required for the cropped image so that after resizing,
    it will fit within the template size with a 200-pixel white border.
    """
    effective_width = template_size[0] - 400
    effective_height = template_size[1] - 400
    width_scale = effective_width / cropped_shape[1]
    height_scale = effective_height / cropped_shape[0]
    scale = min(width_scale, height_scale)
    resized_width = int(cropped_shape[1] * scale)
    resized_height = int(cropped_shape[0] * scale)
    pad_width_total = template_size[0] - resized_width
    pad_height_total = template_size[1] - resized_height
    pad_left = pad_width_total // 2
    pad_right = pad_width_total - pad_left
    pad_top = pad_height_total // 2
    pad_bottom = pad_height_total - pad_top
    return pad_top, pad_bottom, pad_left, pad_right

# Update the batch processing function to use the refined bounding box function

def resize_and_pad(image, template_size):
    """Resize the image while preserving its aspect ratio to fit within the effective area of the template.
    Then, pad the image to match the template size."""
    effective_width = template_size[0] - 100
    effective_height = template_size[1] - 100
    image_aspect = image.shape[1] / image.shape[0]
    effective_aspect = effective_width / effective_height
    if image_aspect > effective_aspect:
        new_width = effective_width
        new_height = int(effective_width / image_aspect)
    else:
        new_height = effective_height
        new_width = int(effective_height * image_aspect)


        # Before the cv2.resize call:
    print(f"Calculated new dimensions: {new_width}x{new_height}")  # Debug print
    if new_width <= 0 or new_height <= 0:
        print(f"Error: Invalid calculated dimensions for resizing: {new_width}x{new_height}")
        return None  # or handle this error appropriately
    
    resized_image = cv2.resize(image, (new_width, new_height))
    pad_top = (template_size[1] - new_height) // 2
    pad_bottom = template_size[1] - new_height - pad_top
    pad_left = (template_size[0] - new_width) // 2
    pad_right = template_size[0] - new_width - pad_left
    padded_image = cv2.copyMakeBorder(resized_image, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    return padded_image


def batch_resize(input_dir, output_dir, template_size, progress_queue):
    """
    Processes all images in the input directory, resizes them based on the provided steps, and updates progress.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get a list of all valid images
    images = [img for img in os.listdir(input_dir) if img.endswith(".jpg") or img.endswith(".png")]
    total_images = len(images)

    for index, image_name in enumerate(images, start=1):
        image_path = os.path.join(input_dir, image_name)
        image = cv2.imread(image_path)
        
        if image is None:  # Check if the image is read correctly
            continue

        # Process the image
        x, y, w, h = find_bounding_box(image)
        cropped_image = image[y:y+h, x:x+w]
        padding = compute_padding(cropped_image.shape[:2], template_size)
        padded_image = cv2.copyMakeBorder(cropped_image, padding[0], padding[1], padding[2], padding[3], cv2.BORDER_CONSTANT, value=[255, 255, 255])
        final_image = resize_and_pad(cropped_image, template_size)
        output_path = os.path.join(output_dir, image_name)
        cv2.imwrite(output_path, final_image)
        
        # Update progress
        progress = (index / total_images) * 100
        progress_queue.put(progress)

    progress_queue.put(100)  # Signal completion



if __name__ == "__main__":
    input_dir = "raw2"
    output_dir = "resized"
    boxed_output_dir = "boxed_outputs"

    batch_resize("raw22", "outputs22(1000x1000)", boxed_output_dir, (1000, 1000)) 
    batch_resize("raw22", "outputs22(1801x2600)", boxed_output_dir, (1801, 2600))  



    boxed_images = os.listdir(boxed_output_dir) if os.path.exists(boxed_output_dir) else []
    boxed_images


