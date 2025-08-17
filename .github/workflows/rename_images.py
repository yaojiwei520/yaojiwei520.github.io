import os
import io
import re
import git
from PIL import Image
from google.cloud import vision

# Constants
IMAGE_FOLDER = os.environ.get('IMAGE_FOLDER', 'images')  # 默认 'image' 目录
MIN_CONFIDENCE = 0.85  # 设置最低置信度

def detect_labels(image_path):
    """Detects labels in an image using the Google Cloud Vision API."""
    try:
        client = vision.ImageAnnotatorClient()
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)
        labels = response.label_annotations
        return labels
    except Exception as e:
        print(f"Error during label detection: {e}")
        return []

def clean_filename(label):
    """Cleans a label to be a valid filename."""
    cleaned_label = re.sub(r'[^\w\s-]', '', label).strip()  # Remove non-alphanumeric
    cleaned_label = re.sub(r'\s+', '-', cleaned_label)       # Replace spaces with hyphens
    return cleaned_label.lower()

def get_image_dimensions(image_path):
    """Gets the dimensions of an image."""
    try:
        img = Image.open(image_path)
        width, height = img.size
        return width, height
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return None, None

def rename_image(image_path):
    """Renames an image based on labels from the Vision API."""
    labels = detect_labels(image_path)
    if not labels:
        print(f"No labels detected for {image_path}, skipping.")
        return False

    # Filter based on confidence and collect labels
    valid_labels = [label.description for label in labels if label.score >= MIN_CONFIDENCE]

    if not valid_labels:
        print(f"No labels with sufficient confidence for {image_path}, skipping.")
        return False

    width, height = get_image_dimensions(image_path)
    if width is None or height is None:
        return False

    # Create new filename
    label_part = '-'.join(clean_filename(label) for label in valid_labels)
    name, ext = os.path.splitext(os.path.basename(image_path))
    new_filename = f"{label_part}-{width}x{height}{ext}"
    new_path = os.path.join(os.path.dirname(image_path), new_filename)

    # Rename file
    try:
        os.rename(image_path, new_path)
        print(f"Renamed '{image_path}' to '{new_path}'")
        return True
    except Exception as e:
        print(f"Error renaming file: {e}")
        return False

def is_git_repository():
    """Check if current directory is a git repository."""
    try:
        git.Repo(".", search_parent_directories=True)
        return True
    except git.InvalidGitRepositoryError:
        return False

def main():
    """Main function to rename images in the specified folder."""
    print("Starting image renaming process...")

    if not is_git_repository():
        print("Not a git repository. Skipping renaming.")
        return
    
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if os.path.isfile(os.path.join(IMAGE_FOLDER, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        print(f"No images found in '{IMAGE_FOLDER}'.")
        return

    renamed_count = 0
    for image_file in image_files:
        image_path = os.path.join(IMAGE_FOLDER, image_file)
        print(f"Processing: {image_file}")  # Added logging
        if rename_image(image_path):
            renamed_count += 1

    print(f"Successfully renamed {renamed_count} images.")

if __name__ == "__main__":
    main()
