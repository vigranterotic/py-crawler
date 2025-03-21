from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
import requests
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor

url = "https://cf.pexnfb.vip/htm_data/2503/16/6721767.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 设置 ChromeDriver 路径
service = Service('C:\\Users\\YourUsername\\Downloads\\chromedriver.exe')
driver = webdriver.Chrome(service=service)


def download_gif(link, index):
    try:
        print(f"正在下载 GIF: {link}")
        gif_response = requests.get(link, headers=headers)
        print(f"下载 GIF 状态码: {gif_response.status_code}")
        gif_response.raise_for_status()
        if not os.path.exists('gifs'):
            os.makedirs('gifs')
        file_path = os.path.join('gifs', f'gif_{index + 1}.gif')
        with open(file_path, 'wb') as f:
            f.write(gif_response.content)
        print(f"成功下载 {file_path}")
    except requests.RequestException as e:
        print(f"下载 {link} 时出错: {e}")


try:
    driver.get(url)

    try:
        # 定位年龄验证链接
        age_verify_link = driver.find_element(By.LINK_TEXT, '__ 滿 18 歲, 請按此 __')
        age_verify_link.click()
        print("已点击年龄验证链接")
    except Exception as e:
        print(f"未找到年龄验证链接或点击失败: {e}")

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    gif_links = []
    # 先找到 class 为 image-big 的 div 元素
    image_big_divs = soup.find_all('div', class_='image-big')
    print(f"找到 {len(image_big_divs)} 个 class 为 image-big 的 div 元素")
    for div in image_big_divs:
        img_tags = div.find_all('img')
        print(f"在当前 div 中找到 {len(img_tags)} 个 img 标签")
        for img in img_tags:
            src = img.get('src')
            if src and src.endswith('.gif'):
                gif_links.append(src)
                print(f"找到 GIF 链接: {src}")

    print(f"共找到 {len(gif_links)} 个 GIF 链接")

    with ThreadPoolExecutor(max_workers=10) as executor:
        for index, link in enumerate(gif_links):
            executor.submit(download_gif, link, index)

except Exception as e:
    print(f"发生错误: {e}")
finally:
    driver.quit()
    