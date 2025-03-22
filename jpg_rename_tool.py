import tkinter as tk
from tkinter import filedialog, messagebox
import os


def rename_jpgs():
    # 选择目录
    directory = filedialog.askdirectory()
    if not directory:
        return

    # 获取用户输入的基础文件名
    base_name = entry.get()
    if not base_name:
        messagebox.showerror("错误", "请输入基础文件名")
        return

    # 获取目录下所有 .jpg 文件
    jpg_files = [f for f in os.listdir(directory) if f.lower().endswith('.jpg')]
    jpg_files.sort()

    # 重命名文件
    for index, file in enumerate(jpg_files, start=1):
        old_path = os.path.join(directory, file)
        new_name = f"{base_name}_{index}.jpg"
        new_path = os.path.join(directory, new_name)
        try:
            os.rename(old_path, new_path)
            print(f"已将 {old_path} 重命名为 {new_path}")
        except Exception as e:
            print(f"重命名 {old_path} 时出错: {e}")

    messagebox.showinfo("完成", "文件重命名完成！")
    root.destroy()  # 添加这行代码来关闭主窗口


# 创建主窗口
root = tk.Tk()
root.title("JPG 文件重命名工具")

# 创建标签和输入框
label = tk.Label(root, text="请输入基础文件名:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

# 创建选择目录并重命名按钮
button = tk.Button(root, text="选择目录并重命名", command=rename_jpgs)
button.pack(pady=20)

# 运行主循环
root.mainloop()
