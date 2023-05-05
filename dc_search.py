"""
该项目为暗链检测系统，只需要在 url.txt 里每行一个 url[http(s)://xx.xx.com/] 即可！
"""
import os
import re

import requests
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup

# 读取 url.txt 文件中的所有 URL
with open('url.txt') as f:
    urls = f.read().splitlines()

with open('rules.txt') as f:
    rules = f.read().splitlines()

log_file = open("logs.txt", 'w')
log_file.write("[+]:找到暗链、[-]:未找到暗链、[E]:发生错误\n\n")


def regex_contents(content):
    for rule in rules:
        pattern = re.compile(rule)
        matched = pattern.findall(content)
        if matched:
            return True, "[" + matched[0] + " * " + str(len(matched)) + "]"
    return False, "未检测到暗链"


def log_requests(url, content, _type):
    flag, content = regex_contents(content)
    if flag:
        message = "[+] " + url + ' ' + content + '\n'
    else:
        message = "[-] " + url + ' ' + content + '\n'

    if _type == "js":
        message = '\t' + message

    log_file.write(message)


def catch_url(_urls):
    for url in _urls:
        print("[U]: ", url)
        # 打开 URL
        try:
            driver.get(url)
        except selenium.common.exceptions.InvalidArgumentException:
            log_file.write("[E] " + url + ' ' + "url 格式错误" + '\n')
            continue
        except selenium.common.exceptions.WebDriverException:
            log_file.write("[E] " + url + ' ' + "url 连接错误" + '\n')
            continue

        # 获取页面 HTML
        html = driver.page_source
        # 匹配首页内容
        log_requests(url, html, "url")

        # 获取所有 js
        soup = BeautifulSoup(html, 'html.parser')
        js_links = [link.get('src') for link in soup.findAll('script') if link.get('src')]

        # 解析每个 JavaScript 文件
        for link in js_links:
            print("\t[J]: ", link)
            # 获取 JavaScript 文件内容
            if not link.startswith('http'):
                link = f'{url}/{link}' if url.endswith('/') else f'{url}/{os.path.basename(url)}/{link}'
            try:
                js_code = requests.get(link).content.decode('utf-8')
                log_requests(link, js_code, "js")
            except requests.exceptions.SSLError:
                log_file.write("\t[E] " + link + ' ' + "js 请求出错" + '\n')
                pass


if __name__ == "__main__":
    # 创建一个 Chrome 浏览器实例，需要下载对应的 ChromeDriver 并配置 PATH 环境变量
    driver = webdriver.Chrome()

    # 遍历 URL
    catch_url(urls)

    # 关闭浏览器实例
    driver.quit()

    log_file.close()
