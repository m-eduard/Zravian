import re
import time
from Framework.utils.Logger import get_projectLogger
from Framework.utils.Constants import BUILDING_SITE_PATTERN, FIRST_BUILDING_SITE_VILLAGE, HTTP_STRING, LAST_BUILDING_SITE_VILLAGE, BuildingType, ResourceFields, get_XPATHS, get_BUILDINGS, get_building_type_by_name
from Framework.utils.SeleniumUtils import clickElement, getCurrentUrl, getElementAttribute, getElementsAttribute, isVisible, get, refresh
from Framework.utils.Utils import time_to_seconds
from Framework.screen.Views import move_to_overview, move_to_village


logger = get_projectLogger()
BUILDINGS = get_BUILDINGS()
XPATH = get_XPATHS()


# Village getters
def find_building(driver, bdType):
    """
    Finds building sites for requested building type.

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
                    logger.error('In function find_building: No attribute href found for element')
                    break
            else:  # If not breaks encountered
                if bdType is BuildingType.Wall and lst:  # Wall appears multiple times
                    lst = lst[:1]
                ret = lst
        else:
            logger.error('In function find_building: Failed to move to corresponding view')
    else:
        logger.error('In function find_building: Invalid parameter bdType')
    return ret


def get_building_level(driver, bdType):
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
                    logger.error('In function get_building_level: No attribute href found for element')
                    break
                elemLvl = None
                levelText = re.search('[1-2]?[0-9]', elem[1])
                if levelText:
                    elemLvl = int(levelText.group())
                else:
                    logger.error('In function get_building_level: No attribute href found for element')
                    break
                lst.append((elemId, elemLvl))
            else:
                if bdType is BuildingType.Wall and lst:  # Wall appears with multiple ids
                    lst = lst[:1]
                lst.sort(key=lambda e: e[1])
                ret = lst
        else:
            logger.error('In function find_building: Failed to move to corresponding view')
    else:
        logger.error('In function get_building_level: Invalid parameter bdType')
    return ret


# Utils
def get_busy_workers_timer(driver):
    """
    Verifies how long untill the workers finish the next building.
    
    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - Int if operation was successful, None otherwise.
    """
    ret = None
    initialURL = getCurrentUrl(driver)
    if initialURL:
        if move_to_overview(driver):
            propList = [XPATH.FINISH_DIALOG, XPATH.INSIDE_TIMER]
            workingTimer = getElementAttribute(driver, propList, 'text')
            if not get(driver, initialURL):
                logger.error('In function get_busy_workers_timer: Failed to return to initial URL')
            else:
                if workingTimer:
                    ret = time_to_seconds(workingTimer[0])
                else:
                    ret = 0
        else:
            logger.error('In function get_busy_workers_timer: Failed to move to overview')
    else:
        logger.error('In function get_busy_workers_timer: Failed to get the current URL')
    return ret


def get_time_to_build(driver, bdType):
    """
    Get the necesary time to construct / upgrade a building.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - Int if operation is successful, None otherwise.
    """
    time_left = None
    if isinstance(bdType, BuildingType):
        if isVisible(driver, XPATH.BUILDING_PAGE_EMPTY_TITLE):
            propList = [XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name, XPATH.CONSTRUCT_COSTS]
            costs = getElementAttribute(driver, propList, 'text')
            if costs:
                costs = costs[0]
                time_left = time_to_seconds(costs.split('|')[-1])
            else:
                logger.error('In function get_time_to_build: Could not find costs')
        else:
            propList = [XPATH.LEVEL_UP_COSTS]
            costs = getElementAttribute(driver, propList, 'text')
            if costs:
                costs = costs[0]
                time_left = time_to_seconds(costs.split('|')[-1].split()[0])
            else:
                logger.error('In function get_time_to_build: Could not find costs')
    else:
        logger.error('In function get_time_to_build: Invalid parameter bdType')
    return time_left


def press_upgrade_button(driver, bdType, waitToFinish=False):
    """
    Press level up building / construct building.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - waitToFinish (Boolean): If True, will wait for building to finish construct,
            False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        if isVisible(driver, XPATH.BUILDING_PAGE_EMPTY_TITLE):
            propList = [XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name, XPATH.CONSTRUCT_BUILDING_ID]
        else:
            propList = [XPATH.LEVEL_UP_BUILDING_BTN]
        initialURL = getCurrentUrl(driver)
        if initialURL:
            time_to_build = max(1, get_time_to_build(driver, bdType))
            if clickElement(driver, propList, refresh=True):
                if waitToFinish:
                    if get(driver, initialURL):
                        time.sleep(time_to_build)
                    else:
                        logger.error('In function press_upgrade_button: Failed to return to initial URL')
                status = True
            else:
                logger.error('In function press_upgrade_button: Unable to press construct / upgrade button')
        else:
            logger.error('In function press_upgrade_button: Failed to get current url')
    else:
        logger.error('In function press_upgrade_button: Invalid parameter bdType')
    return status


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
    moveStatus = False
    if index > 0 and index <= LAST_BUILDING_SITE_VILLAGE:
        if index > 0 and index < FIRST_BUILDING_SITE_VILLAGE:
            moveStatus = move_to_overview(driver)
        elif index >= FIRST_BUILDING_SITE_VILLAGE and index <= LAST_BUILDING_SITE_VILLAGE:
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
                logger.info('In function check_building_page_title: Page does not correspond to building')
        else:
            if isVisible(driver, XPATH.BUILDING_PAGE_TITLE % BUILDINGS[bdType].name):
                status = True
            else:
                logger.info('In function check_building_page_title: Page does not correspond to building')
    else:
        logger.error('In function check_building_page_title: Invalid parameter bdType')
    return status


# Checks
def check_requirements(driver, bdType, forced=False):
    """
    Verifies whether the requirements are fulfilled for building.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - forced (Boolean): If True bypass any inconvenience, False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        requirements = BUILDINGS[bdType].requirements
        for reqBd, reqLevel in requirements:
            reqBdList = get_building_level(driver, reqBd)
            if not reqBdList:  # Construct
                if forced:
                    if not construct_building(driver, reqBd, forced=True, waitToFinish=True):
                        logger.error(f'In function check_requirements: Failed to construct {reqBd}')
                        break
                else:
                    logger.warning(f'In function check_requirements: {reqBd} not found')
                    break
            reqBdList = get_building_level(driver, reqBd)
            # Check level
            if reqBdList[-1][1] < reqLevel:  # Upgrade is required
                if forced:
                    while reqBdList[-1][1] < reqLevel:
                        if not level_up_building_at(driver, reqBdList[-1][0], forced=True, waitToFinish=True):
                            logger.error(f'In function check_requirements: Failed to level up {reqBd}')
                            break
                        reqBdList = get_building_level(driver, reqBd)
                else:
                    logger.warning(f'In function check_requirements: {reqBd} level is too low')
                    break
        else:  # If not break encountered, all requirements are fulfilled
            status = True
    else:
        logger.error('In function check_requirements: Invalid parameter bdType')
    return status


def check_storage(driver, bdType, storageType, forced=False):
    """
    Checks if storage suffice.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - storageType (BuildingType): BuildingType.Warehouse or BuildingType.Granary.
        - forced (Boolean): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        if storageType == BuildingType.Warehouse or storageType == BuildingType.Granary:
            storageXPATH = (XPATH.BUILDING_ERR_WH if storageType == BuildingType.Warehouse else XPATH.BUILDING_ERR_GR)
            propList = []
            if isVisible(driver, XPATH.BUILDING_PAGE_EMPTY_TITLE):
                propList.append(XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name)
            propList.append(storageXPATH)
            if isVisible(driver, propList):
                if forced:
                    storageList = get_building_level(driver, storageType)
                    if not storageList:
                        if not construct_building(driver, storageType, forced=True, waitToFinish=True):
                            logger.error(f'In function check_storage: Failed to construct {storageType}')
                        else:  # Recheck storage
                            status = check_storage(driver, bdType, storageType, forced=True)
                    else:
                        if not level_up_building_at(driver, storageList[-1][0], forced=True, waitToFinish=True):
                            logger.error(f'In function check_storage: Failed to level up {storageType}')
                        else:  # Recheck storage
                            status = check_storage(driver, bdType, storageType, forced=True)
                else:
                    logger.warning(f'In function check_storage: {storageType} not big enough')
            else:
                status = True
        else:
            logger.error('In function check_storage: Invalid parameter storageType')
    else:
        logger.error('In function check_storage: Invalid parameter bdType')
    return status


def check_resources(driver, bdType, forced=False):
    """
    Checks if resources suffice.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - forced (Boolean): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        propList = []
        if isVisible(driver, XPATH.BUILDING_PAGE_EMPTY_TITLE):
            propList.append(XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name)
        propList.append(XPATH.BUILDING_ERR_RESOURCES)
        propList.append(XPATH.INSIDE_TIMER)
        requirementTimer = getElementAttribute(driver, propList, 'text')
        if requirementTimer:
            time_left = time_to_seconds(requirementTimer)
            if forced:
                time.sleep(time_left)
                if refresh(driver):
                    status = check_resources(driver, bdType, forced=True)
                else:
                    logger.error('In function check_resources: Failed to refresh page')
            else:
                logger.warning('In function check_resources: Not enough resources')
        else:
            status = True
    else:
        logger.error('In function check_resources: Invalid parameter bdType')
    return status


def check_busy_workers(driver, bdType, forced=False):
    """
    Checks if workers are not busy.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - forced (Boolean): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        if isVisible(driver, XPATH.BUILDING_ERR_BUSY_WORKERS):
            if forced:
                time_left = get_busy_workers_timer(driver)
                time.sleep(time_left)
                if refresh(driver):
                    status = check_busy_workers(driver, bdType, forced=True)
                else:
                    logger.error('In function check_busy_workers: Failed to refresh page')
            else:
                logger.info('In function check_busy_workers: Workers are busy')
        else:
            status = True
    else:
        logger.error('In function check_busy_workers: Invalid parameter bdType')
    return status


def check_not_max_level(driver, bdType):
    """
    Checks if a building is below its max level.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        if isVisible(driver, XPATH.BUILDING_ERR_MAX_LVL):
            logger.info(f'In function check_not_max_level: {bdType} is at max level')
        else:
            status = True
    else:
        logger.error('In function check_not_max_level: Invalid parameter bdType')
    return status


# Methods
def construct_building(driver, bdType, forced=False, waitToFinish=False):
    """
    Constructs a new building.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - forced (Boolean): If True bypass any inconvenience, False by default.
        - waitToFinish (Boolean): If True, will wait for building to finish construct,
            False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        if bdType in ResourceFields:
            status = True  # Resource fields are already constructed
            logger.info(f'In function construct_building: {BUILDINGS[bdType].name} is in resource fields')
        else:
            if move_to_village(driver):
                # Check for empty place
                emptyPlaces = find_building(driver, BuildingType.EmptyPlace)
                if bdType is BuildingType.RallyPoint or bdType is bdType.Wall:
                    buildings = get_building_level(driver, bdType)
                    if buildings:
                        logger.info(f'In function construct_building: {BUILDINGS[bdType].name} is already constructed')
                        status = True  # Already built
                    else:
                        emptyPlaces = find_building(driver, bdType)
                if not status:
                    if emptyPlaces:
                        if check_requirements(driver, bdType, forced):
                            if enter_building_menu(driver, emptyPlaces[0]) and \
                                    check_building_page_title(driver, BuildingType.EmptyPlace):
                                if check_storage(driver, bdType, BuildingType.Warehouse, forced) and \
                                        check_storage(driver, bdType, BuildingType.Granary, forced):
                                    if check_resources(driver, bdType, forced):
                                        if check_busy_workers(driver, bdType, forced):
                                            # Upgrade
                                            if press_upgrade_button(driver, bdType, waitToFinish=waitToFinish):
                                                status = True
                                            else:
                                                logger.error('In function construct_building: Failed to press\
                                                     upgrade button')
                                        else:
                                            logger.error('In function construct_building: Busy workers check failed')
                                    else:
                                        logger.error('In function construct_building: Resources check failed')
                                else:
                                    logger.error('In function construct_building: Storagecheck failed')
                            else:
                                logger.error('In function construct_building: Entering empty building site failed')
                        else:
                            logger.error('In function construct_building: Requirements check failed')
                    else:
                        logger.error('In function construct_building: Village is full')
            else:
                logger.error('In function construct_building: Failed to move to village')
    else:
        logger.error('In function construct_building: Invalid parameter bdType')
    return status


def level_up_building_at(driver, index, forced=False, waitToFinish=False):
    """
    Levels up a building existing at given index.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - index (Int): Denotes index of building site.
        - forced (Boolean): If True bypass any inconvenience, False by default.
        - waitToFinish (Boolean): If True, will wait for building to finish construct,
            False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if index >= FIRST_BUILDING_SITE_VILLAGE and index <= LAST_BUILDING_SITE_VILLAGE:
        if move_to_village(driver):
            buildingSiteElemText = getElementAttribute(driver, XPATH.BUILDING_SITE_ID % index, 'alt')
            bdType = None
            if buildingSiteElemText:
                buildingSiteRe = re.search('(.*) level', buildingSiteElemText[0])
                if buildingSiteRe:
                    buildingSiteName = buildingSiteRe.group()[:-len('level')]
                    bdType = get_building_type_by_name(buildingSiteName)
                else:
                    logger.error(f'In function level_up_building_at: Element "alt" tag does not respect pattern')
            else:
                logger.error(f'In function level_up_building_at: Element not found')
            if bdType:
                if enter_building_menu(driver, index):
                    if not check_building_page_title(driver, BuildingType.EmptyPlace):
                        if check_not_max_level(driver, bdType) and \
                                check_storage(driver, bdType, BuildingType.Warehouse, forced) and \
                                check_storage(driver, bdType, BuildingType.Granary, forced) and \
                                check_resources(driver, bdType, forced) and \
                                check_busy_workers(driver, bdType, forced):
                            # Upgrade
                            if press_upgrade_button(driver, bdType, waitToFinish=waitToFinish):
                                status = True
                            else:
                                logger.error('In function level_up_building_at: Failed to press upgrade button')
                    else:
                        logger.error(f'In function level_up_building_at: Building site at {index} is empty')
                else:
                    logger.error(f'In function level_up_building_at: Failed to enter building menu {index}')
            else:
                logger.error(f'In function level_up_building_at: Error identifying building type')
        else:
            logger.error('In function level_up_building_at: Failed to move to village')
    else:
        logger.error(f'In function level_up_building_at: Invalid index {index}')
    return status


def demolish_building(driver, bdType):
    """
    Erases a building.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        buildings = get_building_level(driver, bdType)
        if buildings:
            levels = buildings[0][1]
            if move_to_village(driver):
                mainBuildingIndex = find_building(driver, BuildingType.MainBuilding)
                if mainBuildingIndex:
                    mainBuildingIndex = mainBuildingIndex[0]
                    if enter_building_menu(driver, mainBuildingIndex) and \
                            check_building_page_title(driver, BuildingType.MainBuilding):
                        option = clickElement(driver, XPATH.DEMOLITION_BUILDING_OPTION % BUILDINGS[bdType].name)
                        if option:
                            if clickElement(driver, XPATH.DEMOLITION_BTN, refresh=True):
                                propList = [XPATH.FINISH_DIALOG, XPATH.INSIDE_TIMER]
                                demolitionTimer = getElementAttribute(driver, propList, 'text')
                                while demolitionTimer:
                                    demolitionTimer = getElementAttribute(driver, propList, 'text')
                                    if demolitionTimer:
                                        dmTime = max(1, time_to_seconds(demolitionTimer[0]))
                                        time.sleep(dmTime)
                                        print('Will sleep %d' % dmTime)
                                if move_to_village(driver):
                                    status = True
                                else:
                                    logger.error('In function demolish_building: Failed to move to village')
                            else:
                                logger.error('In function demolish_building: Failed to press demolition button')
                        else:
                            logger.error('In function demolish_building: Failed to select demolish option')
                    else:
                        logger.error('In function demolish_building: Failed to enter main building')
                else:
                    logger.error('In function demolish_building: Failed to locate main building')
            else:
                logger.error('In function demolish_building: Failed to move to village view')
        else:
            status = True
    else:
        logger.error('In function demolish_building: Invalid parameter bdType')
    return status


    