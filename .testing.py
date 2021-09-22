# import os
# import json
# from enum import IntEnum, Enum
# from pathlib import Path
import time
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, InvalidSelectorException
from Framework.utility.SeleniumUtils import SWS
from Framework.utility.Constants import CHROME_DRIVER_PATH
# from Framework.utility.SeleniumUtils import get

# def test_get(sws: SWS):
# 	succes = False
# 	sws.get(sws, "cccc")
# 	return succes

sws = SWS(False)
sws.get("https://google.com")

sws.clickElement("/html/body/div[2]/div[2]/div[3]/span/div/div/div[3]/button[2]/div")
sws.sendKeys("/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input", "monkeytype")
sws.clickElement("/html/body/div[1]/div[3]/form/div[1]/div[1]/div[3]/center/input[1]")
