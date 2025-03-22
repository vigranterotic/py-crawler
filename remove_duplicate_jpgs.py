import os
import hashlib
from PIL import Image
import tkinter as tk
from tkinter import filedialog


def calculate_image_hash(image_path):
    """
    计算图像的哈希值
    :param image_path: 图像文件的路径
    :return: 图像的哈希值
    """
    try:
        with Image.open(image_path) as img:
            img = img.resize((100, 100)).convert('RGB')
            img_bytes = img.tobytes()
            hash_object = hashlib.sha256(img_bytes)
            return hash_object.hexdigest()
    except Exception as e:
        print(f"处理 {image_path} 时出错: {e}")
        return None


def remove_duplicate_jpgs(directory):
    """
    清除指定目录中重复的 JPG 文件
    :param directory: 要处理的目录
    """
    hash_dict = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.jpg'):
                file_path = os.path.join(root, file)
                image_hash = calculate_image_hash(file_path)
                if image_hash:
                    if image_hash in hash_dict:
                        print(f"发现重复文件: {file_path}，将被删除")
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            print(f"删除 {file_path} 时出错: {e}")
                    else:
                        hash_dict[image_hash] = file_path


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    target_directory = filedialog.askdirectory()
    if target_directory:
        remove_duplicate_jpgs(target_directory)
    else:
        print("未选择目录。")
    