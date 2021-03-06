import enum
import json
import os
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class LinkShortener(enum.Enum):
    undermined = 0
    unknown = 1
    yoshare = 2
    eductin = 3
    surfsees = 4


class LinkManger:
    def __init__(self, raw_links_page: str, headless: bool = False):

        self.social_networks = ["youtube", "t.me", "facebook"]
        self.shortener_type: LinkShortener = LinkShortener.undermined

        # Link Attributes
        self.raw_links_page = raw_links_page
        self.page_title: str
        self.captcha_links = []
        self.file_links = []

        # Setup browser
        self.browser_data_location = "browser_data"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f'user-data-dir={os.getcwd()}/{self.browser_data_location}')
        if headless:
            self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options, )
        self.wait = WebDriverWait(self.driver, 10)
        # time.sleep(.5)

        # Process Links
        self.driver.get(self.raw_links_page)
        self.__set_page_title()
        self.__set_captcha_links()
        # self.__set_shortener()
        self.__solve_captcha_links()
        self.driver.quit()

    def __set_page_title(self):
        self.page_title = self.driver.title
        print(self.page_title)

    def __set_captcha_links(self, ):

        try:
            links_block = self.driver.find_element(by=By.CSS_SELECTOR, value="*[class='entry-content']").find_elements(
                by=By.TAG_NAME, value='a')

        except NoSuchElementException:
            links_block = self.driver.find_elements(by=By.CSS_SELECTOR, value="a[rel*='noopener']")

        link_elements = [link for link in links_block if
                         not any(social_link in link.get_attribute('href') for social_link in self.social_networks)]

        self.captcha_links = [link.get_attribute('href') for link in link_elements]

    def __set_shortener(self):
        if self.shortener_type == LinkShortener.undermined:
            if LinkShortener.yoshare.name in self.driver.current_url:
                self.shortener_type = LinkShortener.yoshare
            elif LinkShortener.eductin.name in self.driver.current_url:
                self.shortener_type = LinkShortener.eductin
            elif LinkShortener.surfsees.name in self.driver.current_url:
                self.shortener_type = LinkShortener.surfsees
            else:
                self.shortener_type = LinkShortener.unknown
                print(f"Haven't seen this shortener before: {self.driver.current_url}")

    def __solve_captcha_links(self):

        for link in self.captcha_links:
            self.driver.get(link)

            # time.sleep(1)
            # print(self.driver.current_url)

            self.__set_shortener()
            if self.shortener_type == LinkShortener.yoshare:
                destination_link = self.solve_yoshare()
            elif self.shortener_type == LinkShortener.eductin or self.shortener_type == LinkShortener.surfsees:
                destination_link = self.general_solver()
            else:
                destination_link = "Unknown shortener"

            self.file_links.append(destination_link)
            print(self.file_links[-1])

    def solve_yoshare(self, ):
        # Buttons:
        wait = WebDriverWait(self.driver, 20)
        click_here_to_continue_selector = 'input.btn.btn-primary'
        continue_selector = '#btn6'
        get_link_xpath = '/html/body/div[1]/div/div/div[1]/div[6]/a'

        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, click_here_to_continue_selector))).click()
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, continue_selector))).click()
        # time.sleep(4)
        wait.until(ec.element_to_be_clickable((By.XPATH, get_link_xpath))).click()

        # time.sleep(5)
        destination_link = self.get_destination()

        return destination_link

    def general_solver(self, ):
        wait = WebDriverWait(self.driver, 20)

        buttons = ['//*[@id="landing"]', '//*[@id="generater"]', '//*[@id="showlink"]']
        for button in buttons:
            wait.until(ec.element_to_be_clickable((By.XPATH, button))).click()

        destination_link = self.get_destination()
        return destination_link

    def get_destination(self, ):

        # Remove extra tab if exists
        if len(self.driver.window_handles) == 2:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            time.sleep(2)  # Without this a bug occurs

        destination_link: str

        # Solver for DeadIndiaToons
        if "clk.dti.link" in self.driver.current_url:
            get_link_2_xpath = '/html/body/div[1]/div/div/div/div[2]/a'
            self.wait.until(ec.element_to_be_clickable((By.XPATH, get_link_2_xpath))).click()
            destination_link = self.driver.current_url

        # Solver for RareToons
        elif "rtilinks" in self.driver.current_url:
            iframe_css = "iframe[allowfullscreen*='true']"
            destination_link = self.driver.find_element(By.CSS_SELECTOR, iframe_css).get_attribute("src")

        # No Solver yet implemented
        else:
            destination_link = "No valid method found"

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
