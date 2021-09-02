import re
from Framework.utils.Logger import get_projectLogger
from Framework.utils.Constants import BuildingType, get_BUILDINGS, get_XPATHS
from Framework.utils.SeleniumUtils import get, getElementsAttribute, getCurrentUrl, isVisible
from Framework.screen.Views import move_to_overview, move_to_village


# Constants
logger = get_projectLogger()
BUILDINGS = get_BUILDINGS()
XPATH = get_XPATHS()

# List of all resource buildings
ResourceFields = [BuildingType.Woodcutter, BuildingType.ClayPit, BuildingType.IronMine, BuildingType.Cropland]
# HTTP string
HTTP_STRING = 'https://'
# Building site pattern
BUILDING_SITE_PATTERN = '/build.php?id=%d'
# First building site from village
FIRST_BUILDING_SITE_VILLAGE = 19
# Last building site from village
LAST_BUILDING_SITE_VILLAGE = 40


def find_buildings(driver, bdType):
    """
    Finds all building sites ids for requested type.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - List of Ints if operation is successful, None otherwise.
    """
    ret = None
    if isinstance(bdType, BuildingType):
        if bdType in ResourceFields:
            moveStatus = move_to_overview(driver)
        else:
            moveStatus = move_to_village(driver)
        if moveStatus:
            lst = []
            elems = getElementsAttribute(driver, XPATH.BUILDING_SITE_NAME % BUILDINGS[bdType].name, 'href')
            for elem in elems:
                siteIndexText = re.search('id=[0-9]+', elem[0])
                if siteIndexText:
                    lst.append(int(siteIndexText.group()[3:]))
                else:
                    logger.error('In function find_buildings: No attribute href found for element')
                    break
            else:  # If not breaks encountered
                if bdType is BuildingType.Wall and lst:  # Wall appears multiple times
                    lst = lst[:1]
                ret = lst
        else:
            logger.error('In function find_buildings: Failed to move to corresponding view')
    else:
        logger.error('In function find_buildings: Invalid parameter bdType')
    return ret


def find_building(driver, bdType):
    """
    Finds the highest level building with requested type.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - List of Ints if operation is successful, None otherwise.
    """
    ret = None
    retList = find_buildings(driver, bdType)
    if retList:
        ret = retList[0]
    else:
        logger.info('In function find_building: No buildings of required type')
    return ret


def get_building_data(driver, bdType):
    """
    Finds building site id and level for requested buildin type ordered by level.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - List of tuples(Int, Int) if operation is successful, None otherwise.
    """
    ret = None
    if isinstance(bdType, BuildingType):
        if bdType in ResourceFields:
            moveStatus = move_to_overview(driver)
        else:
            moveStatus = move_to_village(driver)
        if moveStatus:
            lst = []
            attributes = ['href', 'alt']
            elems = getElementsAttribute(driver, XPATH.BUILDING_SITE_NAME % BUILDINGS[bdType].name, attributes)
            for elem in elems:
                elemId = None
                siteIndexText = re.search('id=[0-9]+', elem[0])
                if siteIndexText:
                    elemId = int(siteIndexText.group()[3:])
                else:
                    logger.info('In function get_building_data: No attribute href found for element')
                    break
                elemLvl = None
                levelText = re.search('[1-2]?[0-9]', elem[1])
                if levelText:
                    elemLvl = int(levelText.group())
                else:
                    logger.info('In function get_building_data: No attribute alt found for element')
                    break
                lst.append((elemId, elemLvl))
            else:
                if bdType is BuildingType.Wall and lst:  # Wall appears with multiple ids
                    lst = lst[:1]
                lst.sort(key=lambda e: e[1])
                ret = lst
        else:
            logger.error('In function get_building_data: Failed to move to corresponding view')
    else:
        logger.error('In function get_building_data: Invalid parameter bdType')
    return ret


def enter_building_menu(driver, index):
    """
    Enters a building menu.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - index (Int): Denotes building site index.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if index > 0 and index <= LAST_BUILDING_SITE_VILLAGE:
        if index > 0 and index < FIRST_BUILDING_SITE_VILLAGE:
            moveStatus = move_to_overview(driver)
        else:
            moveStatus = move_to_village(driver)
        if moveStatus:
            initialURL = getCurrentUrl(driver)
            if initialURL:
                if initialURL.startswith(HTTP_STRING):
                    newURL = HTTP_STRING + initialURL[len(HTTP_STRING):].split('/', 1)[0] + BUILDING_SITE_PATTERN % index
                    if get(driver, newURL):
                        status = True
                    else:
                        logger.error(f'In function enter_building_menu: Failed to load {newURL}')
                else:
                    logger.error('In function enter_building_menu: Invalid URL format')
            else:
                logger.error('In function enter_building_menu: Failed to retrieve current URL')
        else:
            logger.error('In function enter_building_menu: Failed to change view')
    else:
        logger.error(f'In function enter_building_menu: Invalid parameter index {index}')
    return status


def check_building_page_title(driver, bdType):
    """
    Checks if page title correspons to the building.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if page title corresponds to building, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        if bdType == BuildingType.EmptyPlace:
            if isVisible(driver, XPATH.BUILDING_PAGE_EMPTY_TITLE):
                status = True
            else:
                logger.info(f'In function check_building_page_title: Page does not correspond'
                    f'to building {getCurrentUrl(driver)} and {BUILDINGS[bdType].name}')
        else:
            if isVisible(driver, XPATH.BUILDING_PAGE_TITLE % BUILDINGS[bdType].name):
                status = True
            else:
                logger.info('In function check_building_page_title: Page does not correspond'
                    f'to building {getCurrentUrl(driver)} and {BUILDINGS[bdType].name}')
    else:
        logger.error('In function check_building_page_title: Invalid parameter bdType')
    return status


def time_to_seconds(currTime):
    """
    Converts time in format hh:mm:ss to seconds

    Parameters:
        - currTime (Int): Time in format hh:mm:ss.

    Returns:
        - Equivalent time in seconds.
    """
    SECONDS_IN_HOUR = 3600
    SECONDS_IN_MIN = 3600
    h, m, s = currTime.split(':')
    return int(h) * SECONDS_IN_HOUR + int(m) * SECONDS_IN_MIN + int(s)
