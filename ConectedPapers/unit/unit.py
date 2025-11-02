# -*- coding: utf-8 -*-
import os
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions as Exceptions


def init_driver(address):
    # 创建一个参数对象，用来控制chrome以无界面模式打开，反制selenium采取了监测机制，设置下载目录
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--test-type")  # 禁用沙盒模式
    chrome_options.add_argument("--disable-popup-blocking")  # 禁用弹窗阻止
    # # 不加载图片, 提升速度
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_experimental_option('excludeSwitches',
                                           ['enable-automation'])
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    try:
        # 创建浏览器对象，Chrome驱动放在了Python一样的安装目录
        service = Service(executable_path=address)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # driver = webdriver.Chrome(executable_path=address, chrome_options=chrome_options)

    except Exceptions.SessionNotCreatedException as e:
        print(f"error: {e}")
        raise

    return driver


class Args:
    def __init__(self):
        curr_dir, curr_file_name = os.path.split(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(curr_dir, ".."))

        config = 'config.json'
        config = os.path.join(root_dir, config)
        if not os.path.exists(config):
            print(f'error: without config file.')
            raise None

        # 处理文件参数
        with open(config, 'r', encoding='utf-8') as r:
            self.args_json = json.load(r)

        # 浏览器驱动
        self.driver = init_driver(self.args_json.get('driver'))

        # 查找相关文献迭代次数
        self.iteration = self.args_json.get('iteration', 1)

        # 过滤关键词
        self.filter_keywords = self.args_json.get('filter-keywords', list())

        # 等待时间
        self.wait_time = self.args_json.get('wait-time', 3)

        # 翻译成中文
        self.is_zh = True if self.args_json.get('is-zh', 0) == 1 else False

        # 论文标题合集文件
        self.paper_title_file = self.args_json.get('title-file', 'test.txt')
        paper_title_file_name = self.paper_title_file[:-4]
        paper_file_dir = os.path.join(root_dir, paper_title_file_name)
        if not os.path.exists(paper_file_dir):
            os.makedirs(paper_file_dir)

        self.print_args()

        # 输出文件
        zh = '-zh' if self.is_zh else ''
        self.excel_file = os.path.join(paper_file_dir, f'{paper_title_file_name}{zh}.xlsx')
        self.markdown = os.path.join(paper_file_dir, f'{paper_title_file_name}{zh}.md')

        # 当前主题数据库
        self.database = os.path.join(paper_file_dir, 'database.db')

        # 日志文件
        self.log = os.path.join(paper_file_dir, 'log.txt')
        self.log = Log(self.log)

    def print_args(self):
        print(f'---------------------------------------------')
        print(f'title-file: {self.paper_title_file}')
        print(f'driver: {self.args_json.get("driver")}')
        print(f'iteration: {self.iteration}')
        print(f'filter-keywords: {self.filter_keywords}')
        print(f'wait-time: {self.wait_time}')
        print(f'is-zh: {self.is_zh}')
        print(f'---------------------------------------------')

    def check_is_keyword_in_strings(self, title):
        """
        :func 是并的关系，即所有的关键词都要在标题中出现
        :param title:
        :return:
        """
        # print(self.filter_keywords, title)
        is_exists = True
        for word in self.filter_keywords:
            if word not in title:
                is_exists = False
                break
        return is_exists


class Log:
    def __init__(self, log_file):
        self._file = log_file

    def init(self):
        with open(self._file, "a", encoding="utf-8") as _w:
            _w.write('-----------------------------------------------------\n')
            _w.write('-----------------------------------------------------\n')

    def append(self, message):
        print(message)
        with open(self._file, "a", encoding="utf-8") as _w:
            _str = f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} {message}\n'
            _w.write(_str)


if __name__ == "__main__":
    args = Args()
    # ["predict", "solubility"],
    key = 'metal'
    print(args.check_is_keyword_in_strings(key))
    pass
