import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
import requests
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from collections import Counter

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 设置 ChromeDriver 路径
service = Service('/Users/rouni.yin/Documents/python 小/chromedriver-mac-arm64/chromedriver')


def get_next_index():
    if not os.path.exists('jpgs'):
        return 0
    files = os.listdir('jpgs')
    jpg_files = [f for f in files if f.endswith('.jpg')]
    if not jpg_files:
        return 0
    indices = [int(f.split('_')[1].split('.')[0]) for f in jpg_files]
    return max(indices)


def download_jpg(link, index):
    try:
        print(f"正在下载 JPG: {link}")
        jpg_response = requests.get(link, headers=headers)
        print(f"下载 JPG 状态码: {jpg_response.status_code}")
        jpg_response.raise_for_status()
        if not os.path.exists('jpgs'):
            os.makedirs('jpgs')
        file_path = os.path.join('jpgs', f'jpg_{index + 1}.jpg')
        with open(file_path, 'wb') as f:
            f.write(jpg_response.content)
        print(f"成功下载 {file_path}")
    except requests.RequestException as e:
        print(f"下载 {link} 时出错: {e}")


def find_image_classes(soup):
    all_divs = soup.find_all('div')
    class_counter = Counter()

    for div in all_divs:
        div_class = div.get('class')
        if div_class:
            for c in div_class:
                class_counter[c] += 1

    # 找出出现频率最高的几个 class
    most_common_classes = class_counter.most_common(5)

    # 筛选出包含图片的 class
    image_classes = []
    for class_name, _ in most_common_classes:
        divs_with_class = soup.find_all('div', class_=class_name)
        for div in divs_with_class:
            if div.find('img'):
                image_classes.append(class_name)
                break

    return image_classes


def start_crawling():
    url = entry.get()
    if not url:
        messagebox.showerror("错误", "请输入有效的 URL")
        return
    driver = webdriver.Chrome(service=service)
    try:
        driver.get(url)

        try:
            age_verify_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, '__ 滿 18 歲, 請按此 __'))
            )
            age_verify_link.click()
            print("已点击年龄验证链接")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        except TimeoutException:
            print("在 10 秒内未找到年龄验证链接。")
        except ElementClickInterceptedException:
            print("年龄验证链接存在，但被其他元素遮挡，无法点击。")
        except Exception as e:
            print(f"点击年龄验证链接时发生未知错误: {e}")

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # 自动寻找包含图片的 class
        image_classes = find_image_classes(soup)

        jpg_links = []
        image_big_divs = []
        for class_name in image_classes:
            image_big_divs.extend(soup.find_all('div', class_=class_name))
        print(f"找到 {len(image_big_divs)} 个可能包含图片的 div 元素")
        for div in image_big_divs:
            img_tags = div.find_all('img')
            print(f"在当前 div 中找到 {len(img_tags)} 个 img 标签")
            for img in img_tags:
                src = img.get('src')
                if src and src.endswith('.jpg'):
                    jpg_links.append(src)
                    print(f"找到 JPG 链接: {src}")

        print(f"共找到 {len(jpg_links)} 个 JPG 链接")
        start_index = get_next_index()
        with ThreadPoolExecutor(max_workers=10) as executor:
            for i, link in enumerate(jpg_links):
                executor.submit(download_jpg, link, start_index + i)

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        driver.quit()
        messagebox.showinfo("提示", "图片抓取已完成！")
        root.destroy()  # 关闭 tkinter 主窗口


# 创建主窗口
root = tk.Tk()
root.title("JPG 图片抓取工具")

# 创建标签和输入框
label = tk.Label(root, text="请输入网页 URL:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

# 创建开始按钮
button = tk.Button(root, text="开始抓取", command=start_crawling)
button.pack(pady=20)

# 运行主循环
root.mainloop()
    