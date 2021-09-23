import time
import re
from Framework.screen.HomeUI import get_server, move_to_overview, move_to_village
from Framework.utility.Constants import BuildingType, get_BUILDINGS, get_XPATH, get_building_type_by_name, time_to_seconds
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS


# Project constants
logger = get_projectLogger()
BUILDINGS = get_BUILDINGS()
XPATH = get_XPATH()
# List of all resource buildings
ResourceFields = [BuildingType.Woodcutter, BuildingType.ClayPit, BuildingType.IronMine, BuildingType.Cropland]
# First building site from village
FIRST_BUILDING_SITE_VILLAGE = 19
# Last building site from village
LAST_BUILDING_SITE_VILLAGE = 40
# Min wait time
MIN_WAIT = 1


# Utils
def enter_building_site(sws : SWS, index : int):
    """
    Enters a building menu.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int): Denotes building site index.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    # Building site pattern
    BUILDING_SITE_PATTERN = '/build.php?id=%d'
    if index > 0 and index <= LAST_BUILDING_SITE_VILLAGE:
        if index > 0 and index < FIRST_BUILDING_SITE_VILLAGE:
            moveStatus = move_to_overview(sws)
        else:
            moveStatus = move_to_village(sws)
        if moveStatus:
            server = get_server(sws)
            if server:
                newURL = server.value + BUILDING_SITE_PATTERN % index
                if sws.get(newURL):
                    status = True
                else:
                    logger.error(f'In enter_building_site: Failed to load {newURL}')
            else:
                logger.error('In enter_building_site: Failed to get current server')
        else:
            logger.error('In enter_building_site: Failed to change view')
    else:
        logger.error(f'In enter_building_site: Invalid parameter index {index}')
    return status


def check_building_page_title(sws : SWS, bdType : BuildingType):
    """
    Checks if page title correspons to the building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if page title corresponds to building, False otherwise.
    """
    status = False
    if (bdType == BuildingType.EmptyPlace and sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE)) or \
            bdType != BuildingType.EmptyPlace and sws.isVisible(XPATH.BUILDING_PAGE_TITLE % BUILDINGS[bdType].name):
        status = True
    else:
        logger.info('In check_building_page_title: Page does not correspond'
            f'to building {sws.getCurrentUrl()} and {BUILDINGS[bdType].name}')
    return status


def get_busy_workers_timer(sws : SWS):
    """
    Verifies how long untill the workers finish the next building.
    
    Parameters:
        - sws (SWS): Used to interact with the webpage.

    Returns:
        - Int if operation was successful, None otherwise.
    """
    ret = None
    initialURL = sws.getCurrentUrl()
    if initialURL:
        if move_to_overview(sws):
            propList = [XPATH.FINISH_DIALOG, XPATH.INSIDE_TIMER]
            workingTimer = sws.getElementAttribute(propList, 'text')
            if sws.get(initialURL):
                if workingTimer:
                    ret = time_to_seconds(workingTimer)
                else:
                    ret = 0
            else:
                logger.error('In get_busy_workers_timer: Failed to return to initial URL')
        else:
            logger.error('In get_busy_workers_timer: Failed to move to overview')
    else:
        logger.error('In get_busy_workers_timer: Failed to get the current URL')
    return ret


def get_time_to_build(sws : SWS, bdType : BuildingType):
    """
    Get the necesary time to construct / upgrade a building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - Int if operation is successful, None otherwise.
    """
    time_left = None
    if sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE):
        propList = [XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name, XPATH.CONSTRUCT_COSTS]
        costs = sws.getElementAttribute(propList, 'text')
        try:
            time_left = time_to_seconds(costs.split('|')[-1])
        except (AttributeError, IndexError):
            logger.error('In get_time_to_build: Failed to get time from costs')
    else:
        propList = [XPATH.LEVEL_UP_COSTS]
        costs = sws.getElementAttribute(propList, 'text')
        try:
            time_left = time_to_seconds(costs.split('|')[-1].split()[0])
        except (AttributeError, IndexError):
            logger.error('In get_time_to_build: Failed to get time from costs')
    return time_left


def press_upgrade_button(sws : SWS, bdType : BuildingType, waitToFinish : bool = False):
    """
    Press level up building / construct building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - waitToFinish (bool): If True, will wait for building to finish construct, False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE):
        propList = [XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name, XPATH.CONSTRUCT_BUILDING_ID]
    else:
        propList = [XPATH.LEVEL_UP_BUILDING_BTN]
    initialURL = sws.getCurrentUrl()
    time_to_build = get_time_to_build(sws, bdType)
    if time_to_build:
        time_to_build = max(MIN_WAIT, time_to_build)
        if sws.clickElement(propList, refresh=True):
            if waitToFinish:
                if sws.get(initialURL):
                    logger.info('In press_upgrade_button: Sleep for %d seconds' % time_to_build)
                    time.sleep(time_to_build)
                else:
                    logger.error('In press_upgrade_button: Failed to return to initial URL')
            status = True
        else:
            logger.error('In press_upgrade_button: Unable to press construct / upgrade button')
    else:
        logger.error('In press_upgrade_button: Failed to get time to build')
    return status


def select_and_demolish_building(sws : SWS, index : int):
    """
    On main building`s view selects and demolishes one building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int): Denotes index of building site.

    Returns:
        - True if the operation is successful, False otherwise.    
    """
    status = False
    if check_building_page_title(sws, BuildingType.MainBuilding):
        if sws.clickElement(XPATH.DEMOLITION_BUILDING_OPTION % (str(index) + '.')):
            if sws.clickElement(XPATH.DEMOLITION_BTN, refresh=True):
                propList = [XPATH.FINISH_DIALOG, XPATH.INSIDE_TIMER]
                demolitionTimer = sws.getElementAttribute(propList, 'text')
                # White for demolishing to end
                while demolitionTimer:
                    demolitionTimer = sws.getElementAttribute(propList, 'text')
                    if demolitionTimer:
                        dmTime = max(MIN_WAIT, time_to_seconds(demolitionTimer))
                        time.sleep(dmTime)
                status = True
                logger.success(f'In select_and_demolish_building: Successfully demolished {index}')
            else:
                logger.error('In select_and_demolish_building: Failed to press demolition button')
        else:
            logger.error(f'In select_and_demolish_building: Could not select option {index}')
    else:
        logger.error('In select_and_demolish_building: Main building page not visible')
    return status

# Checks
def check_requirements(sws : SWS, bdType : BuildingType, forced : bool = False):
    """
    Verifies whether the requirements are fulfilled for building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - forced (bool): If True bypass any inconvenience, False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    requirements = BUILDINGS[bdType].requirements
    for reqBd, reqLevel in requirements:
        reqBdList = get_building_data(sws, reqBd)
        if not reqBdList:  # Construct
            if forced:
                if not construct_building(sws, reqBd, forced=True, waitToFinish=True):
                    logger.error(f'In check_requirements: Failed to construct{BUILDINGS[reqBd].name} at'
                        '{reqBd[-1][0]}')
                    break
            else:
                logger.warning(f'In check_requirements: {BUILDINGS[reqBd].name} not found')
                break
        reqBdList = get_building_data(sws, reqBd)
        # Check level
        if reqBdList[-1][1] < reqLevel:  # Upgrade is required
            if forced:
                while reqBdList[-1][1] < reqLevel:
                    if not level_up_building_at(sws, reqBdList[-1][0], forced=True, waitToFinish=True):
                        logger.error(f'In check_requirements: Failed to level up {BUILDINGS[reqBd].name} at'
                            '{reqBd[-1][0]}')
                        break
                    reqBdList = get_building_data(sws, reqBd)
                else:
                    continue  # While finished successfully so the for-iteration did too
                break  # The while failed so the for-iteration failed as well
            else:
                logger.warning(f'In check_requirements: {BUILDINGS[reqBd].name}`s` level is too low')
                break
    else:  # If not break encountered, all requirements are fulfilled
        status = True
    return status


def check_storage(sws : SWS, bdType : BuildingType, storageType : BuildingType, forced : bool = False):
    """
    Checks if storage suffice.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - storageType (BuildingType): BuildingType.Warehouse or BuildingType.Granary.
        - forced (bool): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    initialURL = sws.getCurrentUrl()
    if storageType == BuildingType.Warehouse or storageType == BuildingType.Granary:
        storageXPATH = (XPATH.BUILDING_ERR_WH if storageType == BuildingType.Warehouse else XPATH.BUILDING_ERR_GR)
        propList = []
        if sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE):
            propList.append(XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name)
        propList.append(storageXPATH)
        if sws.isVisible(propList):
            if forced:
                storageList = get_building_data(sws, storageType)
                if not storageList:
                    if not construct_building(sws, storageType, forced=True, waitToFinish=True):
                        logger.error(f'In check_storage: Failed to construct {storageType}')
                    else:  # Recheck storage
                        if sws.get(initialURL):
                            status = check_storage(sws, bdType, storageType, forced=True)
                        else:
                            logger.error('In check_storage: Failed to go back to building')
                else:
                    if not level_up_building_at(sws, storageList[-1][0], forced=True, waitToFinish=True):
                        logger.error(f'In check_storage: Failed to level up {storageType}')
                    else:  # Recheck storage
                        status = check_storage(sws, bdType, storageType, forced=True)
            else:
                logger.warning(f'In check_storage: {storageType} not big enough')
        else:
            status = True
    else:
        logger.error('In check_storage: Invalid parameter storageType')
    return status


def check_resources(sws : SWS, bdType : BuildingType, forced : bool = False):
    """
    Checks if resources suffice.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - forced (bool): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    propList = []
    if sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE):
        propList.append(XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name)
    propList.append(XPATH.BUILDING_ERR_RESOURCES)
    propList.append(XPATH.INSIDE_TIMER)
    requirementTimer = sws.getElementAttribute(propList, 'text')
    if requirementTimer:
        time_left = time_to_seconds(requirementTimer)
        if forced:
            time.sleep(time_left)
            sws.refresh()
            status = check_resources(sws, bdType, forced=True)
        else:
            logger.warning('In check_resources: Not enough resources')
    else:
        status = True
    return status


def check_busy_workers(sws : SWS, bdType : BuildingType, forced : bool = False):
    """
    Checks if workers are not busy.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - forced (bool): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    if sws.isVisible(XPATH.BUILDING_ERR_BUSY_WORKERS):
        if forced:
            time_left = get_busy_workers_timer(sws)
            time.sleep(time_left)
            sws.refresh()
            status = check_busy_workers(sws, bdType, forced=True)
        else:
            logger.warning('In check_busy_workers: Workers are busy')
    else:
        status = True
    return status


def check_not_max_level(sws : SWS, bdType : BuildingType):
    """
    Checks if a building is below its max level.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    if sws.isVisible(XPATH.BUILDING_ERR_MAX_LVL):
        logger.warning(f'In check_not_max_level: {bdType} is at max level')
    else:
        status = True
    return status


# Main methods
def find_building(sws : SWS, bdType : BuildingType):
    """
    Finds the highest level building with requested type.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - List of Ints if operation is successful, None otherwise.
    """
    ret = None
    if bdType != BuildingType.EmptyPlace and bdType != BuildingType.Wall and bdType != BuildingType.RallyPoint:
        retList = get_building_data(sws, bdType)
        if retList:
            ret = retList[-1][0]
        else:
            logger.warning('In find_building: No buildings of required type')
    else:
        retList = find_buildings(sws, bdType)
        if retList:
            ret = retList[0]
        else:
            logger.warning('In find_building: No buildings of required type')
    return ret


def find_buildings(sws : SWS, bdType : BuildingType):
    """
    Finds all building sites ids for requested type.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - List of Ints if operation is successful, None otherwise.
    """
    ret = None
    if bdType in ResourceFields:
        moveStatus = move_to_overview(sws)
    else:
        moveStatus = move_to_village(sws)
    if moveStatus:
        lst = []
        # Finding sites with requested building and retrieving the 'href' to determine the site id
        sitesHref = sws.getElementsAttribute(XPATH.BUILDING_SITE_NAME % BUILDINGS[bdType].name, 'href')
        for href in sitesHref:
            try:
                lst.append(int(re.search('id=([0-9]+)', href).group(1)))
            except (AttributeError, ValueError) as err:
                logger.error(f'In find_buildings: "href" regex failed to return value: {err}')
                break
        else:  # If not breaks encountered
            if bdType is BuildingType.Wall and lst:  # Wall appears multiple times
                lst = lst[:1]
            ret = lst
    else:
        logger.error('In find_buildings: Failed to move to corresponding view')
    return ret


def get_building_data(sws : SWS, bdType : BuildingType):
    """
    Finds building site id and level for requested buildin type ordered by level.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - List of tuples(Int, Int) if operation is successful, None otherwise.
    """
    ret = None
    # Some buildings contain phrase 'Build a' in their name
    NOT_CONSTRUCTED = 'Build a'
    if bdType in ResourceFields:
        moveStatus = move_to_overview(sws)
    else:
        moveStatus = move_to_village(sws)
    if moveStatus:
        lst = []
        attributes = ['href', 'alt']
        # Finding sites with requested building and retrieving the 'href' to determine the site id and
        # 'alt' to determine building level
        sitesAttr = sws.getElementsAttributes(XPATH.BUILDING_SITE_NAME % BUILDINGS[bdType].name, attributes)
        for (href, alt) in sitesAttr:
            try:
                elemId = int(re.search('id=([0-9]+)', href).group(1))
            except (AttributeError, ValueError) as err:
                logger.error(f'In get_building_data: "href" regex failed to return value: {err}')
                break
            try:
                elemLvl = int(re.search('[0-9]+', alt).group())
            except (AttributeError, ValueError) as err:
                if bdType == BuildingType.EmptyPlace:
                    elemLvl = 0
                elif NOT_CONSTRUCTED in alt:
                    continue
                else:
                    logger.error(f'In get_building_data: "alt" regex failed to return value: {err}')
                    break
            # Reached only if both are not None
            lst.append((elemId, elemLvl))
        else:
            if bdType is BuildingType.Wall and lst:  # Wall appears with multiple ids
                lst = lst[:1]
            lst.sort(key=lambda e: e[1])
            ret = lst
    else:
        logger.error('In get_building_data: Failed to move to corresponding view')
    return ret


def get_village_data(sws : SWS):
    """
    Generates a dictionary linking each building to a list of pairs (location, level).

    Parameters:
        - sws (SWS): Used to interact with the webpage.

    Returns:
        - Dictionary if operation is successful, None otherwise.
    """
    ret = None
    buildingsDict = {}
    # First get all resource fields
    for bdType in ResourceFields:
        buildingsDict[bdType] = get_building_data(sws, bdType)
        if buildingsDict[bdType] is None:
            break
    else:
        # Get all buildings
        for bdType in BuildingType:
            if bdType in ResourceFields:
                continue
            buildingsDict[bdType] = get_building_data(sws, bdType)
            if buildingsDict[bdType] is None:
                break
        else:
            ret = buildingsDict
    return ret


def enter_building(sws : SWS, bdType : BuildingType):
    """
    Enters the highest level building of requested type.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    bdId = find_building(sws, bdType)
    if bdId:
        if enter_building_site(sws, bdId) and check_building_page_title(sws, bdType):
            status = True
        else:
            logger.error(f'In enter_building: Failed to enter {bdType} at {bdId}')
    else:
        logger.error(f'In enter_building: {bdType} not found')
    return status


def construct_building(sws : SWS, bdType : BuildingType, forced : bool = False, waitToFinish : bool = False):
    """
    Constructs a new building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - forced (bool): If True bypass any inconvenience, False by default.
        - waitToFinish (bool): If True, will wait for building to finish construct,
            False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if bdType in ResourceFields:
        status = True  # Resource fields are already constructed
    else:
        if move_to_village(sws):
            if check_requirements(sws, bdType, forced):
                # Check for empty place
                toBuildSite = find_building(sws, BuildingType.EmptyPlace)
                if bdType is BuildingType.RallyPoint or bdType is bdType.Wall:
                    buildings = get_building_data(sws, bdType)
                    if buildings:
                        status = True  # Already built
                    else:
                        toBuildSite = find_building(sws, bdType)
                if not status:
                    if toBuildSite:
                        if enter_building_site(sws, toBuildSite):
                            logger.info(f'Attempting to construct {BUILDINGS[bdType].name} at {toBuildSite}')
                            if check_storage(sws, bdType, BuildingType.Warehouse, forced) and \
                                    check_storage(sws, bdType, BuildingType.Granary, forced) and \
                                    check_resources(sws, bdType, forced) and \
                                    check_busy_workers(sws, bdType, forced):
                                # Upgrade
                                if press_upgrade_button(sws, bdType, waitToFinish=waitToFinish):
                                    logger.success('Success building %s' % BUILDINGS[bdType].name)
                                    status = True
                                else:
                                    logger.error('In construct_building: Failed to press\
                                        upgrade button')
                            else:
                                logger.error('In construct_building: Storagecheck failed')
                        else:
                            logger.error('In construct_building: Entering empty building site failed')
                    else:
                        logger.error('In construct_building: Village is full')
                else:
                    logger.warning(f'In construct_building: {BUILDINGS[bdType].name} is already constructed')
            else:
                logger.error('In construct_building: Requirements check failed')
        else:
            logger.error('In construct_building: Failed to move to village')
    return status


def level_up_building_at(sws : SWS, index : int, forced : bool = False, waitToFinish : bool = False):
    """
    Levels up a building existing at given index.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int): Denotes index of building site.
        - forced (bool): If True bypass any inconvenience, False by default.
        - waitToFinish (bool): If True, will wait for building to finish construct,
            False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if index > 0 and index <= LAST_BUILDING_SITE_VILLAGE:
        if index < FIRST_BUILDING_SITE_VILLAGE:
            moveStatus = move_to_overview(sws)
        else:
            moveStatus = move_to_village(sws)
        if moveStatus:
            buildingSiteElemText = sws.getElementAttribute(XPATH.BUILDING_SITE_ID % index, 'alt')
            bdType = None
            if buildingSiteElemText:
                buildingSiteRe = re.search('(.*) level', buildingSiteElemText)
                if buildingSiteRe:
                    buildingSiteName = buildingSiteRe.group()[:-len('level')]
                    bdType = get_building_type_by_name(buildingSiteName)
                else:
                    logger.error(f'In level_up_building_at: Element "alt" tag does not respect pattern')
            else:
                logger.error(f'In level_up_building_at: Element not found')
            if bdType:
                logger.info(f'Attempting to level up {BUILDINGS[bdType].name}')
                if enter_building_site(sws, index):
                    if not check_building_page_title(sws, BuildingType.EmptyPlace):
                        if check_not_max_level(sws, bdType) and \
                                check_storage(sws, bdType, BuildingType.Warehouse, forced) and \
                                check_storage(sws, bdType, BuildingType.Granary, forced) and \
                                check_resources(sws, bdType, forced) and \
                                check_busy_workers(sws, bdType, forced):
                            # Upgrade
                            if press_upgrade_button(sws, bdType, waitToFinish=waitToFinish):
                                logger.success('Success leveling up %s' % BUILDINGS[bdType].name)
                                status = True
                            else:
                                logger.error('In level_up_building_at: Failed to press upgrade button')
                    else:
                        logger.error(f'In level_up_building_at: Building site at {index} is empty')
                else:
                    logger.error(f'In level_up_building_at: Failed to enter building menu {index}')
            else:
                logger.error(f'In level_up_building_at: Error identifying building type')
        else:
            logger.error('In level_up_building_at: Failed to change view')
    else:
        logger.error(f'In level_up_building_at: Invalid index {index}')
    return status


def demolish_building_at(sws : SWS, pos):
    """
    Reduces level of building at index to 0.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int or List of Int): Denotes index(indexes) of building site(s).

    Returns:
        - True if the operation is successful, False otherwise.
    """
    # 40 is not a valid choice, because wall can not be demolished
    status = False
    if isinstance(pos, list):
        wrapper = pos
    else:
        wrapper = [pos]
    mainBuildingIndex = find_building(sws, BuildingType.MainBuilding)
    if mainBuildingIndex:
        if enter_building_site(sws, mainBuildingIndex) and \
                check_building_page_title(sws, BuildingType.MainBuilding):
            if sws.isVisible(XPATH.DEMOLITION_BTN):
                for index in wrapper:
                    if index >= FIRST_BUILDING_SITE_VILLAGE and index < LAST_BUILDING_SITE_VILLAGE:
                        if not select_and_demolish_building(sws, index):
                            logger.error(f'In demolish_building: Failed to select/demolish')
                            break
                    else:
                        logger.error(f'In demolish_building: Invalid index value {index}')
                        break
                else:
                    if move_to_village(sws):
                        status = True
                    else:
                        logger.error('In demolish_building: Failed to move to village')
            else:
                logger.warning('In demolish_building: Level up Main Building first')
        else:
            logger.error('In demolish_building: Failed to enter main building')
    else:
        logger.warning('In demolish_building: Main building not found')
    return status
