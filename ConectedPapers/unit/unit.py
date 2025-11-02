# -*- coding: utf-8 -*-
import os
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions as Exceptions


def init_driver(address):
    # Create a Chrome driver with options, incognito mode, and disable automation flags
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--test-type")  # Disable sandbox mode
    chrome_options.add_argument("--disable-popup-blocking")  # Disable popup blocking
    # # Do not load images to improve speed
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_experimental_option('excludeSwitches',
                                           ['enable-automation'])
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    try:
        # Create browser object, Chrome driver located at specified path
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
            print(f'error: config file not found.')
            raise None

        # Load configuration parameters
        with open(config, 'r', encoding='utf-8') as r:
            self.args_json = json.load(r)

        # Browser driver
        self.driver = init_driver(self.args_json.get('driver'))

        # Number of iterations to search related papers
        self.iteration = self.args_json.get('iteration', 1)

        # Filter keywords
        self.filter_keywords = self.args_json.get('filter-keywords', list())

        # Wait time
        self.wait_time = self.args_json.get('wait-time', 3)

        # Translate to Chinese
        self.is_zh = True if self.args_json.get('is-zh', 0) == 1 else False

        # Paper title collection file
        self.paper_title_file = self.args_json.get('title-file', 'test.txt')
        paper_title_file_name = self.paper_title_file[:-4]
        paper_file_dir = os.path.join(root_dir, paper_title_file_name)
        if not os.path.exists(paper_file_dir):
            os.makedirs(paper_file_dir)

        self.print_args()

        # Output files
        zh = '-zh' if self.is_zh else ''
        self.excel_file = os.path.join(paper_file_dir, f'{paper_title_file_name}{zh}.xlsx')
        self.markdown = os.path.join(paper_file_dir, f'{paper_title_file_name}{zh}.md')

        # Database for current topic
        self.database = os.path.join(paper_file_dir, 'database.db')

        # Log file
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
        :func AND relation: all keywords must appear in the title
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
    # Example keywords: ["predict", "solubility"]
    key = 'metal'
    print(args.check_is_keyword_in_strings(key))
    pass
