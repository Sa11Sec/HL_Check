import os
import random
import re
import time

import requests
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup


class Checker:

    def __init__(self):
        # 创建一个 Chrome 浏览器实例，需要下载对应的 ChromeDriver 并配置 PATH 环境变量
        self.driver = webdriver.Chrome()
        # 读取 urls.txt 文件中的所有 URL
        with open('urls.txt') as f:
            self.urls = f.read().splitlines()
        # 读取 rules.txt 文件中的所有 规则
        with open('rules.txt') as f:
            self.rules = f.read().splitlines()
        # 打开一个日志文件
        log_filename = time.strftime("_%Y-%m-%d_%H-%M-%S_", time.localtime()) + str(random.randint(1000, 9999))
        self.log_file = open("logs" + log_filename + ".txt", 'w')
        self.log_file.write("[+]:找到暗链、[-]:未找到暗链、[E]:发生错误\n\n")

    def __del__(self):
        # 关闭日志文件
        self.log_file.close()

    def start(self):
        # 遍历 URL
        self.check_url()
        # 关闭浏览器实例
        self.driver.quit()

    def regex_contents(self, content):
        for rule in self.rules:
            pattern = re.compile(rule)
            matched = pattern.findall(content)
            if matched:
                return True, "[" + matched[0] + " * " + str(len(matched)) + "]"
        return False, "未检测到暗链"

    def check_url(self):
        for url in self.urls:
            print("[U]: ", url)
            # 打开 URL
            try:
                self.driver.get(url)
            except selenium.common.exceptions.InvalidArgumentException:
                self.log_file.write("[E] " + url + ' ' + "url 格式错误" + '\n')
                continue
            except selenium.common.exceptions.WebDriverException:
                self.log_file.write("[E] " + url + ' ' + "url 连接错误" + '\n')
                continue

            # 获取页面 HTML
            html = self.driver.page_source
            # 匹配首页内容
            self.log_requests(url, html, "url")

            # 获取所有 js
            soup = BeautifulSoup(html, 'html.parser')
            js_links = [link.get('src') for link in soup.findAll('script') if link.get('src')]

            # 解析每个 JavaScript 文件
            for link in js_links:
                print("\t[J]: ", link)
                # 获取 JavaScript 文件内容
                if not link.startswith('http'):
                    link = link.lstrip('.')
                    link = link.lstrip('./')
                    link = link.lstrip('//')
                    link = f'{url}{link}' if url.endswith('/') else f'{url}/{link}'
                try:
                    js_code = requests.get(link).content.decode('utf-8')
                    self.log_requests(link, js_code, "js")
                except requests.exceptions.SSLError:
                    self.log_file.write("\t[E] " + link + ' ' + "js 请求出错" + '\n')
                    pass

    def log_requests(self, url, content, _type):
        flag, content = self.regex_contents(content)
        if flag:
            message = "[+] " + url + ' ' + content + '\n'
        else:
            message = "[-] " + url + ' ' + content + '\n'

        if _type == "js":
            message = '\t' + message

        self.log_file.write(message)


if __name__ == "__main__":
    checker = Checker()
    checker.start()
