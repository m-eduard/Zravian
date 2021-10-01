from enum import Enum
import re
import time
from Framework.infrastructure.buildings import FIRST_BUILDING_SITE_VILLAGE, LAST_BUILDING_SITE_VILLAGE, \
    RESOURCE_FIELDS, find_building
from Framework.screen.Navigation import enter_building, enter_building_site, is_screen_menu_of, \
    move_to_overview, move_to_village
from Framework.utility.Constants import BuildingType, get_XPATH, get_building_info, \
    get_building_type_by_name, get_projectLogger, time_to_seconds
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()
# Min wait time
MIN_WAIT = 1


class BuildingError(Enum):
    """Error codes for constructing / leveling up a building."""
    # Success
    OK = 'Success'
    # Zravian related errors
    MAX_LEVEL_ALREADY = 'Building is already at max level'
    CANT_LEVEL_EMPTY_PLACE = 'Cannot level up empty place'
    FULL_VILLAGE = 'Village is full'
    REQUIREMENTS = 'Requirements are not fulfilled'
    STORAGE = 'Upgrade your storage first'
    RESOURCES = 'Not enough resources'
    BUSY_WORKERS = 'Workers are currently busy'
    # Due to a function unexpected failure
    FATAL_ERROR = 'Unexpected error occured'
    # Main building level is too low
    UPGRADE_MAIN_BUILDING = 'Main building level is too low'


# Utils
def identify_building_type_from_menu(sws: SWS):
    """
    Identifies building type based on current building menu.

    Parameters:
        - sws (SWS): Used to interact with the webpage.

    Returns:
        - BuildingType corresponding to menu if operation is successful, None otherwise.
    """
    ret = None
    if sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE):
        ret = BuildingType.EmptyPlace
    else:
        title = sws.getElementAttribute(XPATH.BUILDING_MENU_TITLE, Attr.TEXT)
        if title:
            bdTitle = None
            # Extract building name from page title
            try:
                bdTitle = re.search('(.*)( level [0-9]+)', title).group(1)
            except AttributeError:
                logger.error(f'In identify_building_menu: Title does not respect pattern: {title}')
            if bdTitle:
                # Translate building name to building type
                bdType = get_building_type_by_name(bdTitle)
                if bdType:
                    ret = bdType
                else:
                    logger.error('In identify_building_menu: get_building_type_by_name() failed')
        else:
            logger.error('In identify_building_menu: Failed to retrieve building title')
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
        - True if operation is successful, False otherwise.
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
                    logger.error('In press_upgrade_button: Failed to enter building in order to wait to finish')
            status = True
        else:
            logger.error('In press_upgrade_button: Failed to press Upgrade')
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
        - True if operation is successful, False otherwise.    
    """
    status = False
    # Zravian event jam text
    ZRAVIAN_EJ_TEXT = '00?'
    # 40 is not a valid choice, because Wall can not be demolished
    if index >= FIRST_BUILDING_SITE_VILLAGE and index < LAST_BUILDING_SITE_VILLAGE:      
        if is_screen_menu_of(sws, BuildingType.MainBuilding):
            if sws.clickElement(XPATH.DEMOLITION_BUILDING_OPTION % index):
                if sws.clickElement(XPATH.DEMOLITION_BTN, refresh=True):
                    propList = [XPATH.FINISH_DIALOG, XPATH.INSIDE_TIMER]
                    demolitionTimer = sws.getElementAttribute(propList, Attr.TEXT)
                    # Wait for demolishing to end
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
                    logger.error('In select_and_demolish_building: Failed to press demolish button')
            else:
                logger.error('In select_and_demolish_building: Failed to select building to demolish')
        else:
            logger.error('In select_and_demolish_building: is_screen_building_site() failed')
    else:
        logger.error(f'In select_and_demolish_building: Invalid index={index}')
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
        - True if operation is successful, False otherwise.
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
    if storageType == BuildingType.Warehouse or storageType == BuildingType.Granary:
        storageXPATH = (XPATH.BUILDING_ERR_WH if storageType == BuildingType.Warehouse else XPATH.BUILDING_ERR_GR)
        propList = []
        # In case of constructing a building check only the required building
        if is_screen_menu_of(sws, BuildingType.EmptyPlace):
            propList.append(XPATH.CONSTRUCT_BUILDING_NAME % get_building_info(bdType).name)
        else:  # Look in costs region
            propList.append(XPATH.LEVEL_UP_ERR_WRAPPER)
        propList.append(storageXPATH)
        # Flag to check if the upgrade happened
        upgraded = False
        if sws.isVisible(propList):
            initialURL = sws.getCurrentUrl()
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
                if upgraded:
                    if sws.get(initialURL):
                        status = check_storage(sws, bdType, storageType, forced)
                    else:
                        logger.error('In check_storage: Failed to return to building menu')
            else:
                logger.warning(f'In check_storage: Upgrade {get_building_info(storageType)} first')
        else:
            status = True
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
    if is_screen_menu_of(sws, BuildingType.EmptyPlace):
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
                    logger.error('In check_busy_workers: Failed to return to building menu')
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
def construct_building(sws: SWS, bdType: BuildingType, forced: bool = False, waitToFinish: bool = False):
    """
    Constructs a new building.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.
        - forced (bool): If True bypass any inconvenience, False by default.
        - waitToFinish (bool): If True, will wait for building to finish construct, False by default.

    Returns:
        - BuildinError.
    """
    status = BuildingError.FATAL_ERROR
    logger.info(f'Attempting to construct {get_building_info(bdType).name}')
    if bdType in RESOURCE_FIELDS:
        status = BuildingError.OK  # Resource fields are already constructed
    else:
        if check_requirements(sws, bdType, forced):
            constructSite = get_construction_site(sws, bdType)
            if constructSite:
                if enter_building_site(sws, constructSite):
                    if check_storage(sws, bdType, BuildingType.Warehouse, forced) and \
                            check_storage(sws, bdType, BuildingType.Granary, forced):
                        if check_resources(sws, bdType, forced):
                            if check_busy_workers(sws, bdType, forced):
                                if press_upgrade_button(sws, bdType, waitToFinish):
                                    logger.success('Successfully built %s' % get_building_info(bdType).name)
                                    status = BuildingError.OK
                                else:
                                    logger.error('In construct_building: press_upgrade_button() failed')
                            else:
                                status = BuildingError.BUSY_WORKERS
                        else:
                            status = BuildingError.RESOURCES
                    else:
                        status = BuildingError.STORAGE
                else:
                    logger.error('In construct_building: enter_building_site() failed')
            else:
                status = BuildingError.FULL_VILLAGE
        else:
            status = BuildingError.REQUIREMENTS
    # Return to Village screen
    if not move_to_village(sws):
        status = BuildingError.FATAL_ERROR
        logger.error('In construct_building: move_to_village() failed')
    if status is not BuildingError.OK:
        logger.info(f'In construct_building: Failed to construct {get_building_info(bdType).name}: {status.value}')
    return status


def level_up_building_at(sws: SWS, index: int, forced: bool = False, waitToFinish: bool = False):
    """
    Levels up a building existing at given index.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int): Denotes index of building site.
        - forced (bool): If True bypass any inconvenience, False by default.
        - waitToFinish (bool): If True, will wait for building to finish construct, False by default.

    Returns:
        - BuildinError.
    """
    status = BuildingError.FATAL_ERROR
    if enter_building_site(sws, index):
        bdType = identify_building_type_from_menu(sws)
        if bdType:
            if bdType is not BuildingType.EmptyPlace:
                logger.info(f'Attempting to level up {get_building_info(bdType).name} at {index}')
                if check_below_max_level(sws, bdType):
                    if check_storage(sws, bdType, BuildingType.Warehouse, forced) and \
                            check_storage(sws, bdType, BuildingType.Granary, forced):
                        if check_resources(sws, bdType, forced):
                            if check_busy_workers(sws, bdType, forced):
                                if press_upgrade_button(sws, bdType, waitToFinish):
                                    logger.success('Successfully leveled up %s' % get_building_info(bdType).name)
                                    status = BuildingError.OK
                                else:
                                    logger.error('In level_up_building_at: press_upgrade_button() failed')
                            else:
                                status = BuildingError.BUSY_WORKERS
                        else:
                            status = BuildingError.RESOURCES
                    else:
                        status = BuildingError.STORAGE
                else:
                    status = BuildingError.MAX_LEVEL_ALREADY
            else:
                status = BuildingError.CANT_LEVEL_EMPTY_PLACE
        else:
            logger.error('In level_up_building_at: identify_building_type_from_menu() failed')
    else:
        logger.error('In level_up_building_at: enter_building_site() failed')
    # Return to Village screen
    if not move_to_village(sws):
        status = BuildingError.FATAL_ERROR
        logger.error('In level_up_building_at: move_to_village() failed')
    if status is not BuildingError.OK:
        logger.info(f'In level_up_building_at: Failed to upgrade {get_building_info(bdType).name}: {status.value}')
    return status


def demolish_building_at(sws: SWS, pos):
    """
    Reduces level of building at index to 0.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int or List of Int): Denotes index(indexes) of building site(s).

    Returns:
        - BuildinError.
    """
    status = BuildingError.FATAL_ERROR
    # Main Building level required to demolish
    DEMOLISH_LVL = 10
    if isinstance(pos, list):
        wrapper = pos
    else:
        wrapper = [pos]
    mb = find_building(sws, BuildingType.MainBuilding)
    if mb and mb.level >= DEMOLISH_LVL:
        if enter_building(sws, BuildingType.MainBuilding):
            if sws.isVisible(XPATH.DEMOLITION_BTN):
                for index in wrapper:
                    if not select_and_demolish_building(sws, index):
                        logger.error(f'In demolish_building: select_and_demolish_building() failed')
                        break
                else:
                    status = True
            else:
                logger.error('In demolish_building: Failed to find demolition button')
        else:
            logger.error('In demolish_building: enter_building() failed')
    else:
        status = BuildingError.UPGRADE_MAIN_BUILDING
    # Return to Village screen
    if not move_to_village(sws):
        status = BuildingError.FATAL_ERROR
        logger.error('In demolish_building: move_to_village() failed')
    if status is not BuildingError.OK:
        logger.info(f'In demolish_building: Failed to demolish {index}: {status.value}')
    return status
