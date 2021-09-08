import re
import time
from Framework.utils.Logger import get_projectLogger
from Framework.utils.Constants import  BuildingType, get_XPATH, get_BUILDINGS, get_building_type_by_name
from Framework.utils.SeleniumUtils import SWS
from Framework.screen.Views import move_to_overview, move_to_village
from Framework.VillageManagement.Utils import FIRST_BUILDING_SITE_VILLAGE, LAST_BUILDING_SITE_VILLAGE, ResourceFields,\
    time_to_seconds, enter_building_menu, check_building_page_title, find_building, find_buildings, get_building_data


logger = get_projectLogger()
BUILDINGS = get_BUILDINGS()
XPATH = get_XPATH()


# Utils
def get_busy_workers_timer(sws : SWS):
    """
    Verifies how long untill the workers finish the next building.
    
    Parameters:
        - sws (SWS): Selenium Web Scraper

    Returns:
        - Int if operation was successful, None otherwise.
    """
    ret = None
    initialURL = sws.getCurrentUrl()
    if initialURL:
        if move_to_overview(sws):
            propList = [XPATH.FINISH_DIALOG, XPATH.INSIDE_TIMER]
            workingTimer = sws.getElementAttribute(propList, 'text')
            if workingTimer:
                while re.search('[^0-9]', workingTimer[0]):
                    workingTimer = sws.getElementAttribute(propList, 'text')
                    time.sleep(1)
            if not sws.get(initialURL):
                logger.error('In get_busy_workers_timer: Failed to return to initial URL')
            else:
                if workingTimer:
                    ret = time_to_seconds(workingTimer[0])
                else:
                    ret = 0
        else:
            logger.error('In get_busy_workers_timer: Failed to move to overview')
    else:
        logger.error('In get_busy_workers_timer: Failed to get the current URL')
    return ret


def get_time_to_build(sws : SWS, bdType):
    """
    Get the necesary time to construct / upgrade a building.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - Int if operation is successful, None otherwise.
    """
    time_left = None
    if isinstance(bdType, BuildingType):
        if sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE):
            propList = [XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name, XPATH.CONSTRUCT_COSTS]
            costsTag = sws.getElementAttribute(propList, 'text')
            if costsTag:
                costs = costsTag[0]
                time_left = time_to_seconds(costs.split('|')[-1])
            else:
                logger.error('In get_time_to_build: Could not find construct costs')
        else:
            propList = [XPATH.LEVEL_UP_COSTS]
            costsTag = sws.getElementAttribute(propList, 'text')
            if costsTag:
                costs = costsTag[0]
                time_left = time_to_seconds(costs.split('|')[-1].split()[0])
            else:
                logger.error('In get_time_to_build: Could not find upgrade costs')
    else:
        logger.error('In get_time_to_build: Invalid parameter bdType')
    return time_left


def press_upgrade_button(sws : SWS, bdType, waitToFinish=False):
    """
    Press level up building / construct building.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - bdType (BuildingType): Denotes a type of building.
        - waitToFinish (Boolean): If True, will wait for building to finish construct,
            False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        if sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE):
            propList = [XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name, XPATH.CONSTRUCT_BUILDING_ID]
        else:
            propList = [XPATH.LEVEL_UP_BUILDING_BTN]
        initialURL = sws.getCurrentUrl()
        if initialURL:
            time_to_build = max(1, get_time_to_build(sws, bdType))
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
            logger.error('In press_upgrade_button: Failed to get current url')
    else:
        logger.error('In press_upgrade_button: Invalid parameter bdType')
    return status


def select_and_demolish_building(sws : SWS, index):
    """
    On main building`s screen selects and demolishes one building.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - index (Int): Denotes index of building site.

    Returns:
        - True if the operation is successful, False otherwise.    
    """
    status = False
    if check_building_page_title(sws, BuildingType.MainBuilding):
        option = sws.clickElement(XPATH.DEMOLITION_BUILDING_OPTION % (str(index) + '.'))
        if option:
            if sws.clickElement(XPATH.DEMOLITION_BTN, refresh=True):
                propList = [XPATH.FINISH_DIALOG, XPATH.INSIDE_TIMER]
                demolitionTimer = sws.getElementAttribute(propList, 'text')
                while demolitionTimer:
                    demolitionTimer = sws.getElementAttribute(propList, 'text')
                    if demolitionTimer:
                        dmTime = max(1, time_to_seconds(demolitionTimer[0]))
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
def check_requirements(sws : SWS, bdType, forced=False):
    """
    Verifies whether the requirements are fulfilled for building.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - bdType (BuildingType): Denotes a type of building.
        - forced (Boolean): If True bypass any inconvenience, False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        requirements = BUILDINGS[bdType].requirements
        for reqBd, reqLevel in requirements:
            reqBdList = get_building_data(sws, reqBd)
            if not reqBdList:  # Construct
                if forced:
                    if not construct_building(sws, reqBd, forced=True, waitToFinish=True):
                        logger.error(f'In check_requirements: Failed to construct {reqBd}')
                        break
                else:
                    logger.warning(f'In check_requirements: {reqBd} not found')
                    break
            reqBdList = get_building_data(sws, reqBd)
            # Check level
            if reqBdList[-1][1] < reqLevel:  # Upgrade is required
                if forced:
                    while reqBdList[-1][1] < reqLevel:
                        if not level_up_building_at(sws, reqBdList[-1][0], forced=True, waitToFinish=True):
                            logger.error(f'In check_requirements: Failed to level up {reqBd}')
                            break
                        reqBdList = get_building_data(sws, reqBd)
                else:
                    logger.warning(f'In check_requirements: {reqBd} level is too low')
                    break
        else:  # If not break encountered, all requirements are fulfilled
            status = True
    else:
        logger.error('In check_requirements: Invalid parameter bdType')
    return status


def check_storage(sws : SWS, bdType, storageType, forced=False):
    """
    Checks if storage suffice.

    Parameters:
        - sws (SWS): Selenium Web Scraper
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
                            status = check_storage(sws, bdType, storageType, forced=True)
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
    else:
        logger.error('In check_storage: Invalid parameter bdType')
    return status


def check_resources(sws : SWS, bdType, forced=False):
    """
    Checks if resources suffice.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - bdType (BuildingType): Denotes a type of building.
        - forced (Boolean): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        propList = []
        if sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE):
            propList.append(XPATH.CONSTRUCT_BUILDING_NAME % BUILDINGS[bdType].name)
        propList.append(XPATH.BUILDING_ERR_RESOURCES)
        propList.append(XPATH.INSIDE_TIMER)
        requirementTimer = sws.getElementAttribute(propList, 'text')
        if requirementTimer:
            time_left = time_to_seconds(requirementTimer[0])
            if forced:
                time.sleep(time_left)
                if sws.refresh():
                    status = check_resources(sws, bdType, forced=True)
                else:
                    logger.error('In check_resources: Failed to refresh page')
            else:
                logger.warning('In check_resources: Not enough resources')
        else:
            status = True
    else:
        logger.error('In check_resources: Invalid parameter bdType')
    return status


def check_busy_workers(sws : SWS, bdType, forced=False):
    """
    Checks if workers are not busy.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - bdType (BuildingType): Denotes a type of building.
        - forced (Boolean): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        if sws.isVisible(XPATH.BUILDING_ERR_BUSY_WORKERS):
            if forced:
                time_left = get_busy_workers_timer(sws)
                time.sleep(time_left)
                if sws.refresh():
                    status = check_busy_workers(sws, bdType, forced=True)
                else:
                    logger.error('In check_busy_workers: Failed to refresh page')
            else:
                logger.info('In check_busy_workers: Workers are busy')
        else:
            status = True
    else:
        logger.error('In check_busy_workers: Invalid parameter bdType')
    return status


def check_not_max_level(sws : SWS, bdType):
    """
    Checks if a building is below its max level.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if the requirement is fullfiled, False otherwise.
    """
    status = False
    if isinstance(bdType, BuildingType):
        if sws.isVisible(XPATH.BUILDING_ERR_MAX_LVL):
            logger.info(f'In check_not_max_level: {bdType} is at max level')
        else:
            status = True
    else:
        logger.error('In check_not_max_level: Invalid parameter bdType')
    return status


# Methods
def construct_building(sws : SWS, bdType, forced=False, waitToFinish=False):
    """
    Constructs a new building.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - bdType (BuildingType): Denotes a type of building.
        - forced (Boolean): If True bypass any inconvenience, False by default.
        - waitToFinish (Boolean): If True, will wait for building to finish construct,
            False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    logger.info('Attempting to construct %s' % BUILDINGS[bdType].name)
    if isinstance(bdType, BuildingType):
        if bdType in ResourceFields:
            status = True  # Resource fields are already constructed
            logger.info(f'In construct_building: {BUILDINGS[bdType].name} is in resource fields')
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
                            if enter_building_menu(sws, toBuildSite):
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
                        logger.info(f'In construct_building: {BUILDINGS[bdType].name} is already constructed')
                else:
                    logger.error('In construct_building: Requirements check failed')
            else:
                logger.error('In construct_building: Failed to move to village')
    else:
        logger.error('In construct_building: Invalid parameter bdType')
    return status


def level_up_building_at(sws, index, forced=False, waitToFinish=False):
    """
    Levels up a building existing at given index.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - index (Int): Denotes index of building site.
        - forced (Boolean): If True bypass any inconvenience, False by default.
        - waitToFinish (Boolean): If True, will wait for building to finish construct,
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
                buildingSiteRe = re.search('(.*) level', buildingSiteElemText[0])
                if buildingSiteRe:
                    buildingSiteName = buildingSiteRe.group()[:-len('level')]
                    bdType = get_building_type_by_name(buildingSiteName)
                else:
                    logger.error(f'In level_up_building_at: Element "alt" tag does not respect pattern')
            else:
                logger.error(f'In level_up_building_at: Element not found')
            if bdType:
                logger.info('Attempting to construct %s' % BUILDINGS[bdType].name)
                if enter_building_menu(sws, index):
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


def demolish_building_at(sws : SWS, index):
    """
    Reduces level of building at index to 0.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - index (Int or List of Int): Denotes index(indexes) of building site(s).

    Returns:
        - True if the operation is successful, False otherwise.
    """
    # 40 is not a valid choice, because wall can not be demolished
    status = False
    if isinstance(index, list):
        wrapper = index
    else:
        wrapper = [index]
    mainBuildingIndex = find_building(sws, BuildingType.MainBuilding)
    if mainBuildingIndex:
        if enter_building_menu(sws, mainBuildingIndex) and \
                check_building_page_title(sws, BuildingType.MainBuilding):
            if sws.isVisible(XPATH.DEMOLITION_BTN):
                for index in wrapper:
                    if index >= FIRST_BUILDING_SITE_VILLAGE and index < LAST_BUILDING_SITE_VILLAGE:
                        if mainBuildingIndex == index:
                            continue
                        if not select_and_demolish_building(sws, index):
                            logger.error(f'In demolish_building: Failed to select/demolish')
                            break
                    else:
                        logger.error(f'In demolish_building: Invalid index value {index}')
                        break
                else:
                    status = True
            else:
                logger.warning('In demolish_building: Level up Main Building first')
        else:
            logger.error('In demolish_building: Failed to enter main building')
    else:
        logger.warning('In demolish_building: Main building not found')
    if not move_to_village(sws):
        logger.error('In demolish_building: Failed to move to village')
    else:
        print('Moved to village')
    return status
