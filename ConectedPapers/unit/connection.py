# -*- coding: utf-8 -*-
import time
from unit.sqlite import Sqlite
from unit.baidu import baidu_trans
# from unit import Args, Sqlite, Log, baidu_trans
from unit import Args, Log
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as Exceptions
from selenium.common.exceptions import WebDriverException

import datetime
import subprocess


def build_graph_from_title(driver: webdriver, title, sqlite: Sqlite, wait_time, log: Log):
    log.append(f'Build graph from title: {title}')
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["pageLoadStrategy"] = "none"
    # driver_path = 'D:/downloads/chromedriver-win64/chromedriver.exe'
    # options = webdriver.ChromeOptions()
    # options.page_load_strategy = 'eager'
    # options.add_experimental_option("useAutomationExtension", False)
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
    try:
        # Relationship graph link
        try:

            res = sqlite.select_url_from_paper(title)
            if len(res) != 0:
                url = res[0][0]
                driver.get(url)
        except WebDriverException:
            print(WebDriverException)
        else:
            # Access the search homepage
            driver.get('https://www.connectedpapers.com/')

            # Enter title
            search_bar = WebDriverWait(driver=driver, timeout=wait_time, poll_frequency=0.5).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/div[1]/div/div/div[1]/div/form/input'))
            )
            search_bar.clear()
            search_bar.send_keys(title)
            # driver.find_elements(By.ID, 'searchbar-input')[1].send_keys(title)

            # Click search
            WebDriverWait(driver=driver, timeout=wait_time, poll_frequency=0.5).until(
                EC.visibility_of_element_located(
                    (By.XPATH,  '//*[@id="desktop-app"]/div[2]/div/div[1]/div/div/div[1]/button')
                )
            ).click()
            # driver.find_element(
            #     By.XPATH,
            #     '//*[@id="desktop-app"]/div[2]/div/div[1]/div/div/div[1]/button').click()

            # print(driver.current_url)

            # Navigate to the search results page
            res = WebDriverWait(driver=driver, timeout=wait_time, poll_frequency=0.5).until(
                EC.visibility_of_all_elements_located((By.TAG_NAME, "article"))
            )
            # res = driver.find_elements(By.TAG_NAME, "article")

            if len(res) != 0:
                # Access the first search result
                res[0].click()

                # url = driver.current_url

            else:
                log.append(f'Warning: without graph information. {title}')
                return []

        # Scrape information based on the link
        return paper_graph_information(driver, sqlite, wait_time, log) # driver,

    except Exceptions.NoSuchElementException as e:
        log.append(f'Warning(build_graph_from_title): paper title: {title}\n{e}')
        return []
    except Exceptions.TimeoutException as e:
        log.append(f'Warning(build_graph_from_title): url failed(TimeoutException) {wait_time}\n{e}')
        return []


def paper_graph_information(driver: webdriver, sqlite: Sqlite, wait_time, log: Log):
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["pageLoadStrategy"] = "none"
    # driver_path = 'D:/downloads/chromedriver-win64/chromedriver.exe'
    # options = webdriver.ChromeOptions()
    # options.page_load_strategy = 'eager'
    # options.add_experimental_option("useAutomationExtension", False)
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
    paper_connection = []
    try:
        log.append(f'Paper graph information: {driver.current_url}')

        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["pageLoadStrategy"] = "none"
        papers = WebDriverWait(driver=driver, timeout=wait_time, poll_frequency=0.5).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, 'authors'))
        )
        # papers = WebDriverWait(driver=driver, timeout=wait_time, poll_frequency=0.5).until(
        #     driver.find_elements(By.CLASS_NAME, 'search authors'))
    # except Exceptions.NoSuchElementException as _:
    #     print(f'Warning(paper_graph_information 1): url failed(NoSuchElementException)')
    #     return []
    # except Exceptions.TimeoutException as _:
    #     print(f'Warning(paper_graph_information 1): url failed(TimeoutException) {wait_time}')
    #     return []
    #
    # try:
        today = datetime.datetime.today()
        # paper_connection = []
        for index, paper in enumerate(papers):
            paper_info = []
            ActionChains(driver).move_to_element(paper).perform()
            a = WebDriverWait(driver=driver, timeout=wait_time, poll_frequency=0.5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[1]/div/a')
                )
            )
            # a = driver.find_element(By.XPATH, '//*[@id="desktop-app"]/div[2]/div[3]/div[3]/div/div[2]/div[1]/div/a')
            title = a.text.strip()
            title = title.replace('"', '')
            if title[-1] == '.':
                title = title[:-1]

            if index == 0 and sqlite.check_title_is_exists_in_graph(title):
                return sqlite.select_connection_from_graph(title)

            # 翻译
            title_zh = baidu_trans(title)
            semantic_scholar_url = a.get_attribute("href")
            paper_info.append(title)
            paper_connection.append(title)
            # print(title)

            if sqlite.check_title_is_exists(title):
                continue

            # Author
            div = driver.find_element(By.XPATH, '//*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[2]/div/div')
            author = div.text.strip()
            paper_info.append(author)
            # year journal
            # //*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[3]/div[1]
            div = driver.find_element(By.XPATH, '//*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[3]/div[1]')
            text = div.text.strip()
            if len(text) <= 4:
                year = text
                journal = ""
            else:
                index_t = 4
                year = text[:index_t].strip()
                journal = text[index_t+1:].strip()
            paper_info.append(year)

            # journal
            paper_info.append(journal)

            # 引用 //*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[4]/div[1]
            div = driver.find_element(By.XPATH, '//*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[4]/div[1]')
            text = div.text.strip()
            index_t = text.find(' ')
            citations = text[:index_t].strip()
            paper_info.append(citations)

            # Average annual citations
            curr_year = today.year  # int type
            try:
                year = int(year)
                citations = int(citations)
                year_citations = citations / (curr_year - year)
            except ValueError:
                year_citations = -1
            except ZeroDivisionError:
                year_citations = citations

            paper_info.append(str(round(year_citations, 2)))

            # 关系图链接
            a = driver.find_element(By.XPATH, '//*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[5]/a')
            connected_papers_url = a.get_attribute("href").strip()
            paper_info.append(connected_papers_url)

            # Semantic Scholar 链接
            paper_info.append(semantic_scholar_url)

            # 文章发布页面 //*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[5]/a[2]
            a = driver.find_element(By.XPATH, '//*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[5]/a[2]')
            publisher_page_url = a.get_attribute("href").strip()
            paper_info.append(publisher_page_url)

            # //*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[7]
            div = driver.find_element(By.XPATH, '//*[@id="desktop-app"]/div[2]/div[4]/div[3]/div/div[2]/div[6]')
            abstract = div.text.strip()
            abstract = abstract.replace('"', '')
            abstract = abstract.replace('\n', '')
            # Translate
            abstract_zh = baidu_trans(abstract)
            # print(abstract)
            # print(driver.find_element(By.XPATH, '//*[@id="desktop-app"]/div[2]/div[3]/div[3]/div/div[2]/div[6]/text()'))
            paper_info.append(abstract)

            # Add translation
            paper_info.append(title_zh)
            paper_info.append(abstract_zh)

            sqlite.insert_paper(paper_info)

            if len(paper_connection) != 41:
                log.append(f'Warning(paper_graph_information): paper connection number is not 41!')
                return False

            # Insert
            sqlite.insert_connection(paper_connection)
            print(sqlite.select_connection_from_graph(paper_connection[0]))
            # Return information
            return sqlite.select_connection_from_graph(paper_connection[0])

            except Exceptions.NoSuchElementException as _:
            log.append(f'Warning(paper_graph_information): url failed(NoSuchElementException)')
            return []

        except Exceptions.TimeoutException as _:
        log.append(f'Warning(paper_graph_information): url failed(TimeoutException) {wait_time}')
        return []

    def bfs(driver: webdriver, titles, iteration, sqlite: Sqlite, wait_time, check_func, log: Log):
        """
        :func Build a complete graph. When extending, decide whether to extend based on filtering conditions.
        """
        log.append('--- Start bfs() ---')
        # driver_path = 'D:/downloads/chromedriver-win64/chromedriver.exe'
        # options = webdriver.ChromeOptions()
        # Configure page load strategy
        # options.page_load_strategy = 'eager'
        # options.add_experimental_option("useAutomationExtension", False)
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)

        for index, item in enumerate(titles):
            if item[-1] == '.':
                item = item[:-1]
            # List as queue, set as visited, dict to record layer
            queue, looked, layer = [item], set(item), {item: 0}

            while len(queue) > 0:
                args = Args()
                driver = args.driver
                title = queue.pop(0)
                log.append(f'Title: {index + 1}-{layer.get(title, 0) + 1}, {title}')

                # Look for neighboring nodes
                res = sqlite.select_connection_from_graph(title)
                if len(res) == 0:
                    # Graph not found, create a new one
                    # Browser driver
                    res = build_graph_from_title(driver, title, sqlite, wait_time, log)
                    driver.close()
                    if len(res) == 0:
                        # Truly not found
                        log.append(f'Warning: no connection: {title}')
                        continue
                    else:
                        log.append(f'Info: build finished.')

                # Find neighboring nodes
                nodes = res[0]
                # Check nodes
                for node in nodes:
                    if check_func(node):
                        if node not in looked and node != title:
                            # Child node
                            if layer.get(title, 0) < iteration - 1:
                                layer[node] = layer.get(title, 0) + 1
                                queue.append(node)
                                looked.add(node)

    def spider(args: Args):
        # Log object
        log = args.log

        # Browser driver
        driver = args.driver

        # Database object
        sqlite = Sqlite(args.database)

        # Read title file
        titles = []
        with open(args.paper_title_file, 'r', encoding='utf-8') as r:
            lines = r.readlines()
            for line in lines:
                if len(line.strip()) == 0:
                    break
                titles.append(line.strip())
            print(titles)

        bfs(driver, titles, args.iteration, sqlite, args.wait_time, args.check_is_keyword_in_strings, log)

        print("Spider finished.")
        driver.close()
        pass
