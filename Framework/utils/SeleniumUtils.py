import time
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from Framework.utils.Logger import get_projectLogger


logger = get_projectLogger()

# Max time for a page to load
MAX_PAGE_LOAD_TIME = 30


@contextmanager
def __waitPageToLoad(driver, timeout=MAX_PAGE_LOAD_TIME):
    """
    Function used to wait for a page refresh.

    Parameters:
        - driver (WebDriver): Interacts with webpages.
        - timeout (Int): Time to wait for page to load.
    """
    try:
        old_page = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, '/html')))
    except TimeoutException:
        logger.error(f'In __waitPageToLoad: Timeout while waiting for current page')
    except NoSuchElementException:
        logger.error(f'In __waitPageToLoad: Failed to find current page')
    assert old_page is not None
    yield
    try:
        WebDriverWait(driver, timeout).until(staleness_of(old_page))
    except TimeoutException:
        logger.error(f'In __waitPageToLoad: Timeout while waiting for new page')
    except NoSuchElementException:
        logger.error(f'In __waitPageToLoad: Failed to find new page')
    assert staleness_of(old_page)


def __seleniumRefreshLock(func):
    """
    Decorator used to avoid "StaleElementReferenceException" in SeleniumUtils functions.

    Parameters:
        - func (Function): Function to call untill the result does not generate StaleElementReferenceException.
    
    Returns:
        - Function wrapper
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
            logger.error(f'In function __seleniumRefreshLock: {func.__name__} returned only stale results')
        return ret
    return inner_func


@__seleniumRefreshLock
def __findElement(driver, prop, method=By.XPATH, waitFor=False):
    """
    Finds a WebElement identified by method and prop.

    Parameters:
        - driver (WebDriver or WebElement): Used to perform find_element().
        - prop (String): Property to search for.
        - method (By): Method used to identify prop, By.XPATH by default.
        - waitFor (Boolean): If True function will wait for element to load, False by default.
    
    Returns:
        - WebElement if operation was successful, None otherwise.
    """
    elem = None
    try:
        if waitFor:
            WebDriverWait(driver, MAX_PAGE_LOAD_TIME).until(EC.element_to_be_clickable((method, prop)))
        elem = driver.find_element(method, prop)
    except TimeoutException:
        logger.warning(f'In __findElement: Element {method}={prop} generated a timeout')
    except NoSuchElementException:
        logger.info(f'In __findElement: Element {method}={prop} not found')
    return elem


@__seleniumRefreshLock
def __findElements(driver, prop, method, waitFor=False):
    """
    Finds WebElements identified by method and prop.

    Parameters:
        - driver (WebDriver or WebElement): Used to perform find_element().
        - prop (String): Property to search for.
        - method (By): Method used to identify prop, By.XPATH by default.
        - waitFor (Boolean): If True function will wait for element to load, False by default.
    
    Returns:
        - List of WebElements found.
    """
    elems = []
    try:
        if waitFor:
            WebDriverWait(driver, MAX_PAGE_LOAD_TIME).until(EC.element_to_be_clickable((method, prop)))
        elems = driver.find_elements(method, prop)
    except TimeoutException:
        logger.warning(f'In __findElements: Element {method}={prop} generated a timeout')
    except NoSuchElementException:
        logger.info(f'In __findElements: Element {method}={prop} not found')
    return elems


def get(driver, URL):
    """
    Loads a webpage.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - URL (String): String denoting URL to load.
    
    Returns:
        - True if operation was successful, False otherwise.
    """
    success = False
    if isinstance(driver, webdriver.Chrome):
        with __waitPageToLoad(driver):
            driver.get(URL)
        if driver.current_url == URL:
            success = True
        else:
            logger.error(f'In function get: Failed to load {URL}')
    else:
        logger.error('In function get: Invalid parameter driver')
    return success


def getCurrentUrl(driver):
    """
    Gets the URL of the current page.
    
    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
    
    Returns:
        - current URL as string.
    """
    ret = None
    if isinstance(driver, webdriver.Chrome):
        ret = driver.current_url
    else:
        logger.error('In function getCurrentUrl: Invalid parameter driver')
    return ret


def refresh(driver):
    """
    Reloads current page.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
    
    Returns:
        - True if operation was successful, False otherwise.
    """
    success = False
    if isinstance(driver, webdriver.Chrome):
        with __waitPageToLoad(driver):
            driver.refresh()
        success = True
    else:
        logger.error('In function refresh: Invalid parameter driver')
    return success


def newTab(driver, URL):
    """
    Creates a new tab with requested URL.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - URL (String): String denoting URL to load.

    Returns:
        - True if operation was successful, False otherwise.
    """
    success = False
    if isinstance(driver, webdriver.Chrome):
        driver.execute_script("window.open('" + URL +"');")
        success = True
    else:
        logger.error('In function newTab: Invalid parameter driver')
    return success
    

def switchToTab(driver, identifier):
    """
    Switches focus to a new tab.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - identifier (Int or String): Index of tab or URL.

    Returns:
        - True if operation was successful, False otherwise.
    """
    success = False
    if isinstance(driver, webdriver.Chrome):
        if isinstance(identifier, int) and identifier < len(driver.window_handles):
            driver.switch_to.window(driver.window_handles[identifier])
            success = True
        elif isinstance(identifier, str):
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if identifier in getCurrentUrl(driver):
                    success = True
                    break
            else:
                logger.error(f'In function switchToTab: Failed to find a tab by identifier {identifier}')
        else:
            logger.error('In function switchToTab: Invalid parameter identifier')
    else:
        logger.error('In function switchToTab: Invalid parameter driver')
    return success


@__seleniumRefreshLock
def isVisible(driver, prop, method=By.XPATH, waitFor=False):
    """
    Checks whether a WebElement is visible.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - prop (String or list of strings): Property to search for.
        - method (By): Method used to identify prop, By.XPATH by default.
        - waitFor (Boolean): If True function will wait for element to load, False by default.

    Returns:
        - True if the element is visible, False otherwise.
    """
    ret = None
    if isinstance(driver, webdriver.Chrome):
        if prop:
            if isinstance(prop, list):
                elem = None
                for currProp in prop[:-1]:
                    driver = __findElement(driver, currProp, method=method, waitFor=waitFor)
                    if not driver:
                        break
                prop = prop[-1]
            if driver:
                elem = __findElement(driver, prop, method=method, waitFor=waitFor)
                ret = (elem != None)
        else:
            logger.error('In function isVisible: Invalid parameter prop')
    else:
        logger.error('In function isVisible: Invalid parameter driver')
    return ret


@__seleniumRefreshLock
def getElementAttribute(driver, prop, attr, method=By.XPATH, waitFor=False):
    """
    Finds a WebElement and returns the value of attr.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - prop (String or list of strings): Property to search for.
        - attr (String or list of strings): Attribute(s) whose value is requested.
        - method (By): Method used to identify prop, By.XPATH by default.
        - waitFor (Boolean): If True function will wait for element to load, False by default.

    Returns:
        - List of Strings with value of the attributes.
    """
    ret = []
    if isinstance(driver, webdriver.Chrome):
        if prop:
            if isinstance(prop, list):
                elem = None
                for currProp in prop[:-1]:
                    driver = __findElement(driver, currProp, method=method, waitFor=waitFor)
                    if not driver:
                        break
                prop = prop[-1]
            if driver:
                elem = __findElement(driver, prop, method=method, waitFor=waitFor)
                if elem:
                    if not isinstance(attr, list):
                        attr = [attr]
                    for at in attr:
                        if at == 'text':
                            ret.append(elem.text)
                        else:
                            ret.append(elem.get_attribute(at))
        else:
            logger.error('In function getElementAttribute: Invalid parameter prop')
    else:
        logger.error('In function getElementAttribute: Invalid parameter driver')
    return ret


@__seleniumRefreshLock
def getElementsAttribute(driver, prop, attr, method=By.XPATH, waitFor=False):
    """
    Finds all corresponding WebElements and returns the value of attr.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - prop (String or list of strings): Property to search for.
        - attr (String or list of strings): Attribute(s) whose value is requested.
        - method (By): Method used to identify prop, By.XPATH by default.
        - waitFor (Boolean): If True function will wait for element to load, False by default.

    Returns:
        - List of Lists of Strings with value of the attributes.
    """
    ret = []
    if isinstance(driver, webdriver.Chrome):
        if prop:
            if isinstance(prop, list):
                elems = []
                for currProp in prop[:-1]:
                    driver = __findElement(driver, currProp, method=method, waitFor=waitFor)
                    if not driver:
                        break
                prop = prop[-1]
            if driver:
                elems = __findElements(driver, prop, method=method, waitFor=waitFor)
                for elem in elems:
                    tmpList = []
                    if not isinstance(attr, list):
                        attr = [attr]
                    for at in attr:
                        if at == 'text':
                            tmpList.append(elem.text)
                        else:
                            tmpList.append(elem.get_attribute(at))
                    ret.append(tmpList)
        else:
            logger.error('In function getElementsAttribute: Invalid parameter prop')
    else:
        logger.error('In function getElementsAttribute: Invalid parameter driver')
    return ret


@__seleniumRefreshLock
def clickElement(driver, prop, refresh=False, method=By.XPATH, waitFor=False, scrollIntoView=False):
    """
    Clicks a WebElement.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - prop (String or list of strings): Property to search for.
        - refresh (Boolean): If True, function will wait for page to reload.
        - method (By): Method used to identify prop, By.XPATH by default.
        - waitFor (Boolean): If True function will wait for element to load, False by default.
        - scrollIntoView (Boolean): If True function will scroll to element, False by default.

    Returns:
        - True if operation was successful, False otherwise.
    """
    success = False
    if isinstance(driver, webdriver.Chrome):
        if prop:
            if isinstance(prop, list):
                for currProp in prop[:-1]:
                    driver = __findElement(driver, currProp, method=method, waitFor=waitFor)
                    if not driver:
                        break
                prop = prop[-1]
            if driver:
                elem = __findElement(driver, prop, method=method, waitFor=waitFor)
                if elem:
                    if scrollIntoView:
                        driver.execute_script("arguments[0].scrollIntoView();", elem)
                    if refresh:
                        with __waitPageToLoad(driver):
                            elem.click()
                    else:
                        elem.click()
                success = True
        else:
            logger.error('In function clickElement: Invalid parameter prop')
    else:
        logger.error('In function clickElement: Invalid parameter driver')
    return success


@__seleniumRefreshLock
def sendKeys(driver, prop, text, method=By.XPATH, waitFor=False):
    """
    Sends text input to input box.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - prop (String or list of strings): Property to search for.
        - text (String): String to insert in the textbox.
        - method (By): Method used to identify prop, By.XPATH by default.
        - waitFor (Boolean): If True function will wait for element to load, False by default.

    Returns:
        - True if operation was successful, False otherwise.
    """
    success = False
    if isinstance(driver, webdriver.Chrome):
        if prop:
            if isinstance(prop, list):
                for currProp in prop[:-1]:
                    driver = __findElement(driver, currProp, method=method, waitFor=waitFor)
                    if not driver:
                        break
                prop = prop[-1]
            if driver:
                elem = __findElement(driver, prop, method=method, waitFor=waitFor)
                if elem:
                    elem.send_keys(text)
                    success = True
        else:
            logger.error('In function sendKeys: Invalid parameter prop')
    else:
        logger.error('In function sendKeys: Invalid parameter driver')
    return success
