import re
import time
from typing import Union
from Framework.screen.HomeUI import get_server, move_to_overview, move_to_village
from Framework.utility.Constants import Building, BuildingType, get_XPATH, get_building_info, \
    get_building_type_by_name, get_projectLogger, time_to_seconds
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
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
def enter_building_site(sws: SWS, index: int):
    """
    Enters a building site.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int): Denotes building site index.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    # Building site URL pattern
    BUILDING_SITE_PATTERN = 'build.php?id=%d'
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
                    logger.error('In enter_building_site: SWS.get() failed')
            else:
                logger.error('In enter_building_site: get_server() failed')
        else:
            logger.error('In enter_building_site: move_to_screen() failed')
    else:
        logger.error(f'In enter_building_site: Invalid parameter index {index}')
    return status


def is_building_menu(sws: SWS, bdType: BuildingType):
    """
    Checks if page corresponds to required building menu.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if page title corresponds to building, False otherwise.
    """
    status = False
    if (bdType == BuildingType.EmptyPlace and sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE)) or \
            bdType != BuildingType.EmptyPlace and \
                sws.isVisible(XPATH.BUILDING_PAGE_TITLE % get_building_info(bdType).name):
        logger.info(f'In is_building_menu: Current screen is {get_building_info(bdType).name} menu')
        status = True
    else:
        logger.info(f'In is_building_menu: Current screen is not {get_building_info(bdType).name} menu')
    return status


def find_building(sws: SWS, bdType: BuildingType):
    """
    Finds the highest level building with requested type.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - Building if operation is successful, None otherwise.
    """
    ret = None
    retList = get_buildings(sws, bdType)
    if retList:
        ret = retList[-1]
    else:
        logger.warning(f'In find_building: No buildings of type {get_building_info(bdType).name}')
    return ret


def get_buildings(sws: SWS, bdType: BuildingType):
    """
    For given building type find all sites, each with corresponding level.

    Will list EmptyPlace with level 0 and Rally Point and Wall as well if not constructed.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - [Building] if operation is successful, None otherwise.
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
        attributes = [Attr.HREF, Attr.ALT]
        # Finding sites with requested building and retrieving the 'href' to determine the site id and
        # 'alt' to determine building level
        sitesAttr = sws.getElementsAttributes(XPATH.BUILDING_SITE_NAME % get_building_info(bdType).name, attributes)
        for (href, alt) in sitesAttr:
            try:
                elemId = int(re.search('id=([0-9]+)', href).group(1))
            except (AttributeError, ValueError) as err:
                logger.error(f'In get_buildings: {Attr.HREF.value} regex failed to return value: {err}')
                break
            try:
                elemLvl = int(re.search('[0-9]+', alt).group())
            except (AttributeError, ValueError) as err:
                # Empty places have level 0 by convention.
                # Rally Point and Wall building places contain their name so they are listed with level 0 too.
                if bdType == BuildingType.EmptyPlace or NOT_CONSTRUCTED in alt:
                    elemLvl = 0
                else:
                    logger.error(f'In get_buildings: {Attr.ALT.value} regex failed to return value: {err}')
                    break
            # Append Building if no error encountered
            lst.append(Building(elemId, elemLvl))
        else:
            if bdType is BuildingType.Wall and lst:  # Wall appears with multiple ids
                lst = lst[:1]
            # Sort ascending by building level
            lst.sort(key=lambda e: int(e[1])) 
            ret = lst
    else:
        logger.error('In get_buildings: move_to_screen() failed')
    return ret


def get_construction_site(sws: SWS, bdType: BuildingType):
    """
    Finds a suitable construction site for building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - Int representing site id if the building may be built, None otherwise.
    """
    ret = None
    if bdType is BuildingType.Wall or bdType is BuildingType.RallyPoint:
        bd = find_building(sws, bdType)
        if bd and bd.level > 0:
            logger.info(f'In get_construction_site: {get_building_info(bdType).name} already constructed')
        else:
            ret = bd.siteId
    else:
        bd = find_building(sws, BuildingType.EmptyPlace)
        if bd:
            ret = bd.siteId
        else:
            logger.info(f'In get_construction_site: Village is full')
    return ret


def get_time_to_build(sws: SWS, bdType: BuildingType, constructingMode: bool = False):
    """
    Get the necesary time to construct / upgrade a building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - Int if operation is successful, None otherwise.
    """
    time_left = None
    if constructingMode:
        propList = [XPATH.CONSTRUCT_BUILDING_NAME % get_building_info(bdType).name, XPATH.CONSTRUCT_COSTS]
        costs = sws.getElementAttribute(propList, Attr.TEXT)
        try:
            time_left = time_to_seconds(costs.split('|')[-1])
        except (AttributeError, IndexError):
            logger.error('In get_time_to_build: Failed to get construct time from costs')
    else:
        propList = [XPATH.LEVEL_UP_COSTS]
        costs = sws.getElementAttribute(propList, Attr.TEXT)
        try:
            time_left = time_to_seconds(costs.split('|')[-1].split()[0])
        except (AttributeError, IndexError):
            logger.error('In get_time_to_build: Failed to get level up time from costs')
    return time_left


def press_upgrade_button(sws: SWS, bdType: BuildingType, waitToFinish: bool = False):
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
    constructingMode = False
    if sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE):
        constructingMode = True
        propList = [XPATH.CONSTRUCT_BUILDING_NAME % get_building_info(bdType).name, XPATH.CONSTRUCT_BUILDING_ID]
    else:
        propList = [XPATH.LEVEL_UP_BUILDING_BTN]
    initialURL = sws.getCurrentUrl()
    # Extract time to build
    time_to_build = get_time_to_build(sws, bdType, constructingMode)
    if time_to_build is not None:
        time_to_build = max(MIN_WAIT, time_to_build)
        if sws.clickElement(propList, refresh=True):
            if waitToFinish:
                if sws.get(initialURL):
                    logger.info('In press_upgrade_button: Sleep for %d seconds' % time_to_build)
                    time.sleep(time_to_build)
                else:
                    logger.error('In press_upgrade_button: SWS.get() failed')
            status = True
        else:
            logger.error('In press_upgrade_button: SWS.clickElement() failed')
    else:
        logger.error('In press_upgrade_button: Failed to get time to build')
    return status


def select_and_demolish_building(sws: SWS, index: int):
    """
    On main building`s view selects and demolishes one building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int): Denotes index of building site.

    Returns:
        - True if the operation is successful, False otherwise.    
    """
    # Zravian event jam text
    ZRAVIAN_EJ_TEXT = '00?'
    status = False
    if is_building_menu(sws, BuildingType.MainBuilding):
        if sws.clickElement(XPATH.DEMOLITION_BUILDING_OPTION % index):
            if sws.clickElement(XPATH.DEMOLITION_BTN, refresh=True):
                propList = [XPATH.FINISH_DIALOG, XPATH.INSIDE_TIMER]
                demolitionTimer = sws.getElementAttribute(propList, Attr.TEXT)
                # White for demolishing to end
                while demolitionTimer:
                    demolitionTimer = sws.getElementAttribute(propList, Attr.TEXT)
                    if demolitionTimer:
                        if ZRAVIAN_EJ_TEXT in demolitionTimer:
                            demolitionTimer = ''.join([char for char in demolitionTimer if char != '?'])
                            sws.refresh()
                        dmTime = max(MIN_WAIT, time_to_seconds(demolitionTimer))
                        time.sleep(dmTime)
                logger.success(f'In select_and_demolish_building: Successfully demolished {index}')
                status = True
            else:
                logger.error('In select_and_demolish_building: SWS.clickElement() failed')
        else:
            logger.error('In select_and_demolish_building: SWS.clickElement() failed')
    else:
        logger.error('In select_and_demolish_building: is_building_menu() failed')
    return status


# Checks
def check_requirements(sws: SWS, bdType: BuildingType, forced: bool = False):
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
    # Check building disponibility
    disponibility = False
    otherBuilding = find_building(sws, bdType)
    if otherBuilding and otherBuilding.level > 0:
        if get_building_info(bdType).duplicates and \
                otherBuilding.level == get_building_info(bdType).maxLevel:
            logger.info(f'In check_requirements: Able to construct another {get_building_info(bdType).name}')
            disponibility = True
        else:
            logger.info(f'In check_requirements: Unable to construct another {get_building_info(bdType).name}')
    else:
        disponibility = True
    # Verify building requirements
    if disponibility:
        requirements = get_building_info(bdType).requirements
        for reqBd, reqLevel in requirements:
            # Ensure its constructed
            bd = find_building(sws, reqBd)
            if not bd or bd.level == 0:
                if forced:
                    if not construct_building(sws, reqBd, True, True):
                        logger.error('In check_requirements: construct_building() failed')
                        break
                else:
                    logger.warning(f'In check_requirements: {get_building_info(reqBd).name} not found')
                    break
            # Verify requirement level
            bd = find_building(sws, reqBd)
            while bd.level < reqLevel:
                if forced:
                    if not level_up_building_at(sws, bd.siteId, True, True):
                        logger.error('In check_requirements: level_up_building_at() failed')
                        break
                    bd = find_building(sws, reqBd)
                else:
                    logger.warning(f'In check_requirements: {get_building_info(reqBd).name}`s` level is too low')
                    break
            else:
                # No breaks encountered so go to the next iteration
                continue
            # Any break in the while will lead to this break
            break
        else:
            # All requirements fulfilled
            status = True
    return status


def check_storage(sws: SWS, bdType: BuildingType, storageType: BuildingType, forced: bool = False):
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
        # In case of constructing a building check only the required building
        if is_building_menu(sws, BuildingType.EmptyPlace):
            propList.append(XPATH.CONSTRUCT_BUILDING_NAME % get_building_info(bdType).name)
        else:  # Look in costs region
            propList.append(XPATH.LEVEL_UP_ERR_WRAPPER)
        propList.append(storageXPATH)
        # Flag to check if the upgrade happened
        upgraded = False
        if sws.isVisible(propList):
            if forced:
                logger.info(f'In check_storage: Will upgrade {get_building_info(storageType).name}')
                storageBuilding = find_building(sws, storageType)
                if not storageBuilding:
                    # Attempt to construct storage building
                    if not construct_building(sws, storageType, True, True):
                        logger.error('In check_storage: construct_building() failed')
                    else:
                        upgraded = True
                else:
                    if not level_up_building_at(sws, storageBuilding.siteId, True, True):
                        logger.error('In check_storage: level_up_building_at() failed')
                    else:
                        upgraded = True
            else:
                logger.warning(f'In check_storage: Upgrade {get_building_info(storageType)} first')
        else:
            status = True
        if sws.get(initialURL):
            # If a building was upgraded
            if not status and upgraded:
                status = check_storage(sws, bdType, storageType, forced)
        else:
            logger.error('In check_storage: SWS.get() failed')
    else:
        logger.error(f'In check_storage: Invalid parameter storageType={storageType}')
    return status


def check_resources(sws: SWS, bdType: BuildingType, forced: bool = False):
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
    # In case of constructing a building check only the required building
    if is_building_menu(sws, BuildingType.EmptyPlace):
        propList.append(XPATH.CONSTRUCT_BUILDING_NAME % get_building_info(bdType).name)
    propList += [XPATH.BUILDING_ERR_RESOURCES, XPATH.INSIDE_TIMER]
    requirementTimer = sws.getElementAttribute(propList, Attr.TEXT)
    if requirementTimer:
        time_left = time_to_seconds(requirementTimer)
        if forced:
            logger.info(f'In check_resources: Waiting {time_left} for resources')
            time.sleep(time_left)
            sws.refresh()
            status = check_resources(sws, bdType, True)
        else:
            logger.warning('In check_resources: Not enough resources')
    else:
        status = True
    return status


def check_busy_workers(sws: SWS, bdType: BuildingType, forced: bool = False):
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
            time_left = 0
            # Get refference to current building
            initialURL = sws.getCurrentUrl()
            if move_to_overview(sws):
                propList = [XPATH.FINISH_DIALOG, XPATH.INSIDE_TIMER]
                workingTimer = sws.getElementAttribute(propList, Attr.TEXT)
                # Return to building menu
                if sws.get(initialURL):
                    # Check for how long are the workers busy
                    if workingTimer:
                        time_left = time_to_seconds(workingTimer)
                else:
                    logger.error('In check_busy_workers: SWS.get() failed')
            else:
                logger.error('In check_busy_workers: move_to_overview() failed')
            if time_left:
                logger.info(f'In check_busy_workers: Waiting {time_left} for workers')
                time.sleep(time_left)
                sws.refresh()
                status = check_busy_workers(sws, bdType, True)
        else:
            logger.warning('In check_busy_workers: Workers are busy')
    else:
        status = True
    return status


def check_below_max_level(sws: SWS, bdType: BuildingType):
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
        logger.warning(f'In check_below_max_level: {get_building_info(bdType).name} is at max level')
    else:
        status = True
    return status


# Main methods
def enter_building(sws: SWS, bdType: BuildingType):
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
        if enter_building_site(sws, bdId.siteId) and is_building_menu(sws, bdType):
            status = True
        else:
            logger.error(f'In enter_building: Failed to enter {get_building_info(bdType).name} at {bdId}')
    else:
        logger.warning(f'In enter_building: {get_building_info(bdType).name} not found. Ensure its constructed')
    return status


def get_village_data(sws: SWS) -> dict:
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
        buildingsDict[bdType] = get_buildings(sws, bdType)
        if buildingsDict[bdType] is None:
            break
    else:
        # Get all buildings
        for bdType in BuildingType:
            if bdType in ResourceFields:
                continue
            buildingsDict[bdType] = get_buildings(sws, bdType)
            if bdType == BuildingType.RallyPoint or bdType == BuildingType.Wall:
                if buildingsDict[bdType][0].level == 0:
                    buildingsDict[bdType] = []
            if buildingsDict[bdType] is None:
                break
        else:
            ret = buildingsDict
    return ret


def construct_building(sws: SWS, bdType: BuildingType, forced: bool = False, waitToFinish: bool = False):
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
    logger.info(f'Attempting to construct {get_building_info(bdType).name}')
    if bdType in ResourceFields:
        status = True  # Resource fields are already constructed
    else:
        if check_requirements(sws, bdType, forced):
            if move_to_village(sws):
                constructSite = get_construction_site(sws, bdType)
                if constructSite:
                    if enter_building_site(sws, constructSite):                            
                        if check_storage(sws, bdType, BuildingType.Warehouse, forced) and \
                                check_storage(sws, bdType, BuildingType.Granary, forced) and \
                                check_resources(sws, bdType, forced) and \
                                check_busy_workers(sws, bdType, forced):
                            # Upgrade
                            if press_upgrade_button(sws, bdType, waitToFinish=waitToFinish):
                                logger.success('Successfully built %s' % get_building_info(bdType).name)
                                status = True
                            else:
                                logger.error('In construct_building: Failed to press upgrade button')
                    else:
                        logger.error('In construct_building: enter_building_site() failed')
                else:
                    logger.warning('In construct_building: get_construction_site() failed')
            else:
                logger.error('In construct_building: move_to_village() failed')
        else:
            logger.warning('In construct_building: check_requirements() failed')
    if not status:
        logger.info(f'In construct_building: Failed to construct {get_building_info(bdType).name}')
    return status


def level_up_building_at(sws: SWS, index: int, forced: bool = False, waitToFinish: bool = False):
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
            buildingSiteElemText = sws.getElementAttribute(XPATH.BUILDING_SITE_ID % index, Attr.ALT)
            bdType = None
            # Get building type
            if buildingSiteElemText:
                buildingSiteRe = re.search('(.*) level', buildingSiteElemText)
                if buildingSiteRe:
                    buildingSiteName = buildingSiteRe.group()[:-len('level')]
                    bdType = get_building_type_by_name(buildingSiteName)
                else:
                    logger.error(f'In level_up_building_at: Element`s {Attr.ALT.value} tag does not respect pattern')
            else:
                logger.error(f'In level_up_building_at: SWS.getElementAttribute() failed')
            if bdType:
                logger.info(f'Attempting to level up {get_building_info(bdType).name} at {index}')
                if enter_building_site(sws, index):
                    if not is_building_menu(sws, BuildingType.EmptyPlace):
                        if check_below_max_level(sws, bdType) and \
                                check_storage(sws, bdType, BuildingType.Warehouse, forced) and \
                                check_storage(sws, bdType, BuildingType.Granary, forced) and \
                                check_resources(sws, bdType, forced) and \
                                check_busy_workers(sws, bdType, forced):
                            # Upgrade
                            if press_upgrade_button(sws, bdType, waitToFinish=waitToFinish):
                                logger.success('Successfully leveled up %s' % get_building_info(bdType).name)
                                status = True
                            else:
                                logger.error('In level_up_building_at: press_upgrade_button() failed')
                    else:
                        logger.error(f'In level_up_building_at: Building site at {index} is empty')
                else:
                    logger.error('In level_up_building_at: enter_building_site() failed')
            else:
                logger.error(f'In level_up_building_at: Failed to identify building type at {index}')
        else:
            logger.error('In level_up_building_at: move_to_screen() failed')
    else:
        logger.error(f'In level_up_building_at: Invalid index={index}')
    if not status:
        logger.info(f'In level_up_building_at: Failed to level up {get_building_info(bdType).name}')
    return status


def demolish_building_at(sws: SWS, pos):
    """
    Reduces level of building at index to 0.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int or List of Int): Denotes index(indexes) of building site(s).

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if isinstance(pos, list):
        wrapper = pos
    else:
        wrapper = [pos]
    if enter_building(sws, BuildingType.MainBuilding):
        if sws.isVisible(XPATH.DEMOLITION_BTN):
            for index in wrapper:
                # 40 is not a valid choice, because Wall can not be demolished
                if index >= FIRST_BUILDING_SITE_VILLAGE and index < LAST_BUILDING_SITE_VILLAGE:
                    if not select_and_demolish_building(sws, index):
                        logger.error(f'In demolish_building: Failed to select/demolish')
                        break
                else:
                    logger.error(f'In demolish_building: Invalid index={index}')
                    break
            else:
                if move_to_village(sws):
                    status = True
                else:
                    logger.error('In demolish_building: move_to_village() failed')
        else:
            logger.warning('In demolish_building: Level up Main Building first')
    else:
        logger.error('In demolish_building: enter_building() failed')
    return status
