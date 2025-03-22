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


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 设置 ChromeDriver 路径
service = Service('/Users/rouni.yin/Documents/python 小/chromedriver-mac-arm64/chromedriver')


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

        jpg_links = []
        image_big_divs = soup.find_all('div', class_='tpc_content do_not_catch')
        print(f"找到 {len(image_big_divs)} 个 class 为 image-big 的 div 元素")
        for div in image_big_divs:
            img_tags = div.find_all('img')
            print(f"在当前 div 中找到 {len(img_tags)} 个 img 标签")
            for img in img_tags:
                src = img.get('src')
                if src and src.endswith('.jpg'):
                    jpg_links.append(src)
                    print(f"找到 JPG 链接: {src}")

        print(f"共找到 {len(jpg_links)} 个 JPG 链接")

        with ThreadPoolExecutor(max_workers=10) as executor:
            for index, link in enumerate(jpg_links):
                executor.submit(download_jpg, link, index)

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        driver.quit()


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
    
