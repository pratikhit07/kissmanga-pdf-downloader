import os
import codecs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

chrome_driver = os.path.join(os.getcwd(), "chromedriver_linux64/chromedriver")
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

delay = 30  # seconds


def write_debug_info(filename):
    if not os.path.isdir('debug'):
        os.makedirs('debug')

    driver.get_screenshot_as_file("debug/%s.png" % filename)
    with codecs.open('debug/%s.html' % filename, 'w', "utf-8") as f:
        f.write(driver.page_source)


def get_chapters_list_html(url):
    driver.get(url)
    write_debug_info('chapter_list1')
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'listing')))
        print "Page is ready!"
        write_debug_info('chapter_list2')
        return driver.page_source
    except TimeoutException:
        print "Loading took too much time! -- listing"


def get_image_urls(url):
    driver.get(url)
    write_debug_info('chapter_details1')
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'divImage')))
        write_debug_info('chapter_details2')
        return driver.execute_script("return lstImages")
    except TimeoutException:
        print "Loading took too much time! -- divImage"
    return []
