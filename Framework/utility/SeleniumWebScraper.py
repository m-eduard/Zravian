from contextlib import contextmanager
from enum import Enum
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, InvalidSelectorException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait
from Framework.utility.Constants import CHROME_DRIVER_PATH, get_projectLogger


# Project constants
logger = get_projectLogger()

# Max time for a page to load
MAX_PAGE_LOAD_TIME = 5


# Attributes to be retrieved for a WebElement
class Attr(Enum):
    ALT = 'alt'
    CLASS = 'class'
    HREF = 'href'
    ID = 'id'
    TEXT = 'text'
    TITLE = 'title'
    VALUE = 'value'


class SWS:
    def __init__(self, headless : bool):
        options = webdriver.ChromeOptions()
        if headless:  # Set headless = False in order to see the browser
            options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('start-maximized')
        options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH)

    def close(self):
        """Close WebDriver."""
        if self.driver:
            self.driver.quit()
        self.driver = None

    def __seleniumRefreshLock(func):
        """
        Used as decorator to avoid "StaleElementReferenceException" in SeleniumWebScraper functions.

        Parameters:
            - func (Function): Function to call.
        
        Returns:
            - A new function body for func. (Recalling func if StaleElementReferenceException is encountered). 
        """
        def inner_func(*args, **kwargs):
            ret = None
            stale = True
            startTime = time.time()
            endTime = startTime + MAX_PAGE_LOAD_TIME
            while stale and startTime < endTime:
                stale = False
                startTime = time.time()
                try:
                    ret = func(*args, **kwargs)
                except StaleElementReferenceException:
                    stale = True
            if startTime >= endTime:
                logger.error(f'In __seleniumRefreshLock: {func.__name__} returned only stale results')
            return ret
        return inner_func

    @__seleniumRefreshLock
    def __findElement(driver : WebDriver, prop : str, waitFor : bool = False):
        """
        Finds a WebElement identified by xpath and prop.

        Parameters:
            - driver (WebDriver or WebElement): Used to perform find_element().
            - prop (str): Property to search for.
            - waitFor (bool): If True function will wait for element to load, False by default.
        
        Returns:
            - WebElement if operation was successful, None otherwise.
        """
        elem = None
        try:
            if waitFor:
                WebDriverWait(driver, MAX_PAGE_LOAD_TIME).until(EC.element_to_be_clickable((By.XPATH, prop)))
            elem = driver.find_element_by_xpath(prop)
        except TimeoutException:
            logger.error(f'In __findElement: Element {prop} generated a timeout')
        except NoSuchElementException:
            logger.info(f'In __findElement: Element {prop} not found')
        except InvalidSelectorException:
            logger.error(f'In __findElement: Syntax {prop} is not a properly defined xpath expression')
        return elem

    @__seleniumRefreshLock
    def __findElements(driver : WebDriver, prop : str, waitFor : bool = False):
        """
        Finds WebElements identified by xpath and prop.

        Parameters:
            - driver (WebDriver or WebElement): Used to perform find_element().
            - prop (str): Property to search for.
            - waitFor (bool): If True function will wait for element to load, False by default.
        
        Returns:
            - [WebElements].
        """
        elems = []
        try:
            if waitFor:
                WebDriverWait(driver, MAX_PAGE_LOAD_TIME).until(EC.element_to_be_clickable((By.XPATH, prop)))
            elems = driver.find_elements_by_xpath(prop)
        except TimeoutException:
            logger.warning(f'In __findElements: Element {prop} generated a timeout')
        except NoSuchElementException:
            logger.info(f'In __findElements: Element {prop} not found')
        except InvalidSelectorException:
            logger.error(f'In __findElement: Syntax {prop} is not a properly defined xpath expression')
        return elems

    @contextmanager
    def __waitPageToLoad(self, timeout : int = MAX_PAGE_LOAD_TIME):
        """
        Used to wait for a page refresh.

        Parameters:
            - timeout (Int): Time to wait for page to load.
        """
        # Get current page refference
        try:
            old_page = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, '/html')))
        except TimeoutException:
            logger.error(f'In __waitPageToLoad: Timeout while waiting for current page')
        except NoSuchElementException:
            logger.error(f'In __waitPageToLoad: Failed to find current page')
        # Ensure the refference is valid
        assert old_page is not None
        yield
        # Waitt for the refference to become stale
        try:
            WebDriverWait(self.driver, timeout).until(staleness_of(old_page))
        except TimeoutException:
            logger.error(f'In __waitPageToLoad: Timeout while waiting for new page')
        except NoSuchElementException:
            logger.error(f'In __waitPageToLoad: Failed to find new page')
        # Ensure the refference is now stale
        assert staleness_of(old_page)

    def get(self, URL : str, checkURL : bool = True):
        """
        Loads a webpage.

        Parameters:
            - URL (str): String denoting URL to load.
            - checkURL (bool): If True verifies the link once loaded, True by default.
        
        Returns:
            - True if operation was successful, False otherwise.
        """
        success = False
        with self.__waitPageToLoad():
            self.driver.get(URL)
        if self.driver.current_url == URL or not checkURL:
            success = True
        else:
            logger.error(f'In get: Failed to load {URL}')
        return success

    def getCurrentUrl(self):
        """
        Gets the URL of the current page.
        
        Returns:
            - Current URL as string.
        """
        return str(self.driver.current_url)

    def refresh(self, hardRefesh : bool = False):
        """
        Reloads current page.

        Parameters:
            - hardRefresh (bool): Closes and reopens tab.
        """
        if not hardRefesh:
            self.driver.refresh()
        else:
            # Opens a new tab with same URL and closes the first
            initialURL = self.getCurrentUrl()
            self.newTab(initialURL)
            self.driver.close()
            self.switchToTab(initialURL)

    def newTab(self, URL : str, switchTo : bool = False):
        """
        Creates a new tab with requested URL.

        Parameters:
            - URL (str): String denoting URL to load.
            - switchTo (bool): If True will move to the new tab, False by default.

        Returns:
            - True if operation was successful, False otherwise.
        """
        success = False
        self.driver.execute_script("window.open('" + URL +"');")
        if switchTo:
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                # identify the new tab by URL
                if URL in self.getCurrentUrl():
                    success = True
                    break
            else:
                logger.error(f'In newTab: Failed to find a tab by identifier {URL}')
        else:
            success = True
        return success
    
    def switchToTab(self, identifier):
        """
        Switches focus to a tab.

        Parameters:
            - identifier (Int or String): Index of tab or URL.

        Returns:
            - True if operation was successful, False otherwise.
        """
        success = False
        if isinstance(identifier, int) and identifier < len(self.driver.window_handles):
            self.driver.switch_to.window(self.driver.window_handles[identifier])
            success = True
        elif isinstance(identifier, str):
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if identifier in self.getCurrentUrl():
                    success = True
                    break
            else:
                logger.error(f'In switchToTab: Failed to find a tab by identifier {identifier}')
        else:
            logger.error('In switchToTab: Invalid parameter identifier')
        return success

    def enter_iframe(self, frameIdentifier : str):
        """
        Enters a frame identified by string.

        Parameters:
            - frameIdentifier (str): String to identify frame. 
        """
        self.driver.switch_to_frame(frameIdentifier)

    def exit_iframe(self):
        """Exits iframes, goes to default content."""
        self.driver.switch_to_default_content()

    @__seleniumRefreshLock
    def propList_to_driver_and_prop(self, prop : list, waitFor : bool):
        """
        Based on a list of properties finds the WebElement identified by all properties but the last.
        Returns it and the last property.

        Parameters:
            - prop ([str]): Property to search for.
            - waitFor (bool): If True function will wait for element to load, False by default.

        Returns:
            - WebElement, str.
        """
        tmp_driver = self.driver
        # Separate last property from the other properties
        *identifiers, lastProp = prop
        # Incrementally compute driver based on all properties except the last one
        for currProp in identifiers:
            tmp_driver = SWS.__findElement(tmp_driver, currProp, waitFor)
            if not tmp_driver:
                break
        return tmp_driver, lastProp

    @__seleniumRefreshLock
    def isVisible(self, prop, waitFor : bool = False):
        """
        Checks whether a WebElement is visible.

        Parameters:
            - prop (str or [str]): Property to search for.
            - waitFor (bool): If True function will wait for element to load, False by default.

        Returns:
            - True if the element is visible, False otherwise.
        """
        success = False
        if prop:
            tmp_driver = self.driver
            if isinstance(prop, list):
                tmp_driver, prop = self.propList_to_driver_and_prop(prop, waitFor)
            if tmp_driver:
                elem = SWS.__findElement(tmp_driver, prop, waitFor)
                if elem != None:
                    success = True
        else:
            logger.error('In isVisible: Invalid parameter prop')
        return success

    @__seleniumRefreshLock
    def getElementAttribute(self, prop, attr : Attr, waitFor : bool = False):
        """
        Finds a WebElement and returns the value of attr.

        Parameters:
            - prop (str or [str]): Property to search for.
            - attr (Attr): Attribute whose value is requested.
            - waitFor (bool): If True function will wait for element to load, False by default.

        Returns:
            - String with value of attribute, None if WebElement does not have attribute.
        """
        ret = None
        if prop:
            retList = self.getElementAttributes(prop, [attr], waitFor)
            if retList:
                ret = retList[0]
        else:
            logger.error('In getElementAttribute: Invalid parameter prop')
        return ret

    @__seleniumRefreshLock
    def getElementAttributes(self, prop, attr : list, waitFor : bool = False):
        """
        Finds a WebElement and returns list with value of attr.

        Parameters:
            - prop (str or [str]): Property to search for.
            - attr ([Attr]): Attribute(s) whose value is requested.
            - waitFor (bool): If True function will wait for element to load, False by default.

        Returns:
            - [str].
        """
        ret = []
        if prop:
            tmp_driver = self.driver
            if isinstance(prop, list):
                tmp_driver, prop = self.propList_to_driver_and_prop(prop, waitFor)
            if tmp_driver:
                elem = SWS.__findElement(tmp_driver, prop, waitFor)
                if elem:
                    for at in attr:
                        if at.value == 'text':
                            ret.append(elem.text)
                        else:
                            ret.append(elem.get_attribute(at.value))
                    ret = [str(e) for e in ret]
        else:
            logger.error('In getElementAttributes: Invalid parameter prop')
        return ret

    @__seleniumRefreshLock
    def getElementsAttribute(self, prop, attr : Attr, waitFor : bool = False):
        """
        Finds all corresponding WebElements and returns the value of attr.

        Parameters:
            - prop (str or [str]): Property to search for.
            - attr (Attr): Attribute whose value is requested.
            - waitFor (bool): If True function will wait for element to load, False by default.

        Returns:
            - [str], value of attr for each element.
        """
        ret = []
        if prop:
            retList = self.getElementsAttributes(prop, [attr], waitFor)
            if retList:
                ret = [retElem[0] for retElem in retList]
        else:
            logger.error('In getElementsAttribute: Invalid parameter prop')
        return ret

    @__seleniumRefreshLock
    def getElementsAttributes(self, prop, attr : list, waitFor : bool = False):
        """
        Finds all corresponding WebElements and returns the value of attr.

        Parameters:
            - prop (str or [str]): Property to search for.
            - attr ([str]): Attribute(s) whose value is requested.
            - waitFor (bool): If True function will wait for element to load, False by default.

        Returns:
            - [[str]], a list with all attributes for each element.
        """
        ret = []
        if prop:
            tmp_driver = self.driver
            if isinstance(prop, list):
                tmp_driver, prop = self.propList_to_driver_and_prop(prop, waitFor)
            if tmp_driver:
                elems = SWS.__findElements(tmp_driver, prop, waitFor)
                for elem in elems:
                    tmpList = []
                    for at in attr:
                        if at.value == 'text':
                            tmpList.append(elem.text)
                        else:
                            tmpList.append(elem.get_attribute(at.value))
                    ret.append(tmpList)
        else:
            logger.error('In getElementsAttributes: Invalid parameter prop')
        return ret

    @__seleniumRefreshLock
    def clickElement(self, prop, refresh : bool = False, waitFor : bool = False,
                scrollIntoView : bool =False, javaScriptClick=False):
        """
        Clicks a WebElement.

        Parameters:
            - prop (str or [str]): Property to search for.
            - refresh (bool): If True, function will wait for page to reload. False by default.
            - waitFor (bool): If True function will wait for element to load, False by default.
            - scrollIntoView (bool): If True function will scroll to element, False by default.
            - javaScriptClick (bool): If True will click by using a JS script, False by default.

        Returns:
            - True if operation was successful, False otherwise.
        """
        success = False
        if prop:
            tmp_driver = self.driver
            if isinstance(prop, list):
                tmp_driver, prop = self.propList_to_driver_and_prop(prop, waitFor)
            if tmp_driver:
                elem = SWS.__findElement(tmp_driver, prop, waitFor)
                if elem:
                    if scrollIntoView:
                        tmp_driver.execute_script("arguments[0].scrollIntoView();", elem)
                    if refresh:
                        with self.__waitPageToLoad():
                            if javaScriptClick:
                                self.driver.execute_script("arguments[0].click();", elem)
                            else:
                                elem.click()
                    else:
                        if javaScriptClick:
                            self.driver.execute_script("arguments[0].click();", elem)
                        else:
                            elem.click()
                    success = True
                else:
                    logger.error(f'In clickElement: Failed to click element identified by {prop}')
        else:
            logger.error('In clickElement: Invalid parameter prop')
        return success

    @__seleniumRefreshLock
    def sendKeys(self, prop, text : str, waitFor : bool = False):
        """
        Sends text input to input box.

        Parameters:
            - prop (str or [str]): Property to search for.
            - text (str): String to insert in the textbox.
            - waitFor (bool): If True function will wait for element to load, False by default.

        Returns:
            - True if operation was successful, False otherwise.
        """
        success = False
        if prop:
            tmp_driver = self.driver
            if isinstance(prop, list):
                tmp_driver, prop = self.propList_to_driver_and_prop(prop, waitFor)
            if tmp_driver:
                elem = SWS.__findElement(tmp_driver, prop, waitFor)
                if elem:
                    if text is None:
                        elem.clear()
                    else:
                        elem.send_keys(text)
                    success = True
                else:
                    logger.error(f'In sendKeys: Failed to send keys to element identified by {prop}')
        else:
            logger.error('In sendKeys: Invalid parameter prop')
        return success
