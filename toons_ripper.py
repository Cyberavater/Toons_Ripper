import json
import os
import time
import enum

import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class LinkShortener(enum.Enum):
    undermined = 0
    unknown = 1
    yoshare = 2
    eductin = 3
    surfsees = 4


class LinkParser:
    def __init__(self, raw_links_page: str, ):
        # raw_links_page

        self.raw_links_page = raw_links_page
        req = requests.get(self.raw_links_page)
        self.soup = BeautifulSoup(req.text, "html.parser")
        self.title: str = self.soup.select_one(" header > div > h1").string

    def link_scraper(self):
        captcha_links = []

        links_element = self.soup.find_all(any, {"style": "text-align: center;"})

        for item in links_element:

            link_element = item.select_one("a")
            previous_element = link_element.previous_sibling

            if previous_element:
                weird_shit = previous_element.text.split(' :', 1)[0],
                name = weird_shit[0]
            else:
                name = link_element.text

            link = link_element.get('href')

            captcha_links.append({
                'name': name,
                'link': link,
            })

        return captcha_links


class LinkManger:
    def __init__(self, captcha_links: list):
        self.shortener_type: LinkShortener = LinkShortener.undermined
        self.captcha_links = captcha_links
        self.browser_data_location = "browser_data"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f'user-data-dir={os.getcwd()}/{self.browser_data_location}')
        self.options.add_argument("--headless")

    def __set_shortener(self, driver):
        if self.shortener_type == LinkShortener.undermined:
            if LinkShortener.yoshare.name in driver.current_url:
                self.shortener_type = LinkShortener.yoshare
            elif LinkShortener.eductin.name in driver.current_url:
                self.shortener_type = LinkShortener.eductin
            elif LinkShortener.surfsees.name in driver.current_url:
                self.shortener_type = LinkShortener.surfsees
            else:
                self.shortener_type = LinkShortener.unknown
                print(f"Haven't seen this shortener before: {driver.current_url}")

    def get_links(self):
        file_links = []
        with webdriver.Chrome(options=self.options, ) as driver:
            # wait = WebDriverWait(driver, 20)

            time.sleep(1)

            for link in self.captcha_links:
                driver.get(link['link'])

                time.sleep(1)

                self.__set_shortener(driver)
                if self.shortener_type == LinkShortener.yoshare:
                    destination_link = self.solve_yoshare(driver)
                elif self.shortener_type == LinkShortener.eductin or self.shortener_type == LinkShortener.surfsees:
                    destination_link = self.general_solver(driver)

                file_links.append({
                    "name": link['name'],
                    "link": destination_link,
                })
                print(file_links[-1])

            return file_links

    def get_destination(self, driver, wait):

        if len(driver.window_handles) == 2:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        if "rtilinks" in driver.current_url:
            get_download_link_xpath = '/html/body/section/div/div/div/center/a'
            watch_online_iframe_xpath = '/html/body/iframe[2]'
            watch_online_xpath = '//*[@id="download-hidden"]/a'

            if "quick" in driver.current_url:
                wait.until(ec.element_to_be_clickable((By.XPATH, get_download_link_xpath))).click()
                wait.until(ec.frame_to_be_available_and_switch_to_it((By.XPATH, watch_online_iframe_xpath)))
                wait.until(ec.element_to_be_clickable((By.XPATH, watch_online_xpath))).click()
            # elif "fast" in driver.current_url:
            else:
                wait.until(ec.element_to_be_clickable((By.XPATH, get_download_link_xpath))).click()
        elif self.shortener_type == LinkShortener.yoshare:
            get_link_2_xpath = '/html/body/div[1]/div/div/div/div[2]/a'
            wait.until(ec.element_to_be_clickable((By.XPATH, get_link_2_xpath))).click()

        destination_link = driver.current_url

        return destination_link

    def solve_yoshare(self, driver):
        # Buttons:
        wait = WebDriverWait(driver, 20)
        click_here_to_continue_selector = '#yuidea > input.btn.btn-primary'
        continue_selector = '#btn6'
        get_link_xpath = '/html/body/div[1]/div/div/div[1]/div[6]/a'

        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, click_here_to_continue_selector))).click()
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, continue_selector))).click()
        time.sleep(4)
        wait.until(ec.element_to_be_clickable((By.XPATH, get_link_xpath))).click()
        time.sleep(5)

        destination_link = self.get_destination(driver, wait)
        return destination_link

    def general_solver(self, driver):
        wait = WebDriverWait(driver, 20)

        buttons = ['//*[@id="landing"]/div[2]/center/img', '//*[@id="generater"]/img', '//*[@id="showlink"]']
        for button in buttons:
            wait.until(ec.element_to_be_clickable((By.XPATH, button))).click()

        destination_link = self.get_destination(driver, wait)
        return destination_link


class FileIO:
    def __init__(self, filename: str, file_links: list, output_folder: str = 'output', ):
        self.file_links = file_links
        self.output_folder = output_folder
        self.filename = filename

    def write_file(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print("Output Folder Created")
        counter = 0
        while os.path.isfile(f"{self.output_folder}/{self.filename}{counter if counter else ''}.json"):
            counter += 1
        filename = f"{self.output_folder}/{self.filename}{counter if counter else ''}.json"
        with open(filename, "w") as outfile:
            # print(self.file_links)
            json.dump(self.file_links, outfile)
            print(f"Links extracted in output folder: {filename}")
