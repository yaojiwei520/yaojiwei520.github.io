import os
import io
from google.cloud import vision
from PIL import Image
import datetime
import git

# 你的 image 文件夹路径
IMAGE_FOLDER = 'images'

def analyze_image(image_path):
    """使用 Google Cloud Vision API 分析图片."""
    try:
        client = vision.ImageAnnotatorClient()

        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.label_detection(image=image)
        labels = response.label_annotations

        # 提取标签并组合成文件名
        label_names = [label.description for label in labels]
        new_filename = '_'.join(label_names[:3])  # 使用前三个标签
        return new_filename
    except Exception as e:
        print(f"Error analyzing image {image_path}: {e}")
        return None

def rename_image(image_path):
    """重命名图片."""
    try:
        new_filename = analyze_image(image_path)
        if new_filename:
            file_extension = os.path.splitext(image_path)[1]
            new_path = os.path.join(os.path.dirname(image_path), f"{new_filename}{file_extension}")

            if image_path != new_path:
                # 防止文件名冲突
                counter = 1
                while os.path.exists(new_path):
                    name, ext = os.path.splitext(new_path)
                    new_path = f"{name}_{counter}{ext}"  # 增加计数器
                    counter += 1

                os.rename(image_path, new_path)
                print(f"Renamed '{image_path}' to '{new_path}'")
                return True
            else:
                print(f"No changes for {image_path}")
                return False
        else:
            print(f"Could not analyze {image_path}")
            return False
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def main():
    """主函数."""
    renamed_files = False
    for filename in os.listdir(IMAGE_FOLDER):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            image_path = os.path.join(IMAGE_FOLDER, filename)
            if os.path.isfile(image_path): # 检查是否是文件
                if rename_image(image_path):
                    renamed_files = True

    if not renamed_files:
        print("No images were renamed.")
        exit()

if __name__ == "__main__":
    main()
