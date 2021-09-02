from Framework.utils.Constants import BuildingType
from Framework.VillageManagement.Utils import enter_building_menu, find_building
from Framework.utils.Logger import ProjectLogger


logger = ProjectLogger()


# Entering functions
def enter_academy(driver):
    """
    Enters Academy.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    academyId = find_building(driver, BuildingType.Academy)
    if academyId:
        if enter_building_menu(driver, academyId):
            status = True
        else:
            logger.error('In function enter_academy: Failed to enter building')
    else:
        logger.warning('In function enter_academy: Academy not found')
    return status


def enter_barracks(driver):
    """
    Enters Barracks.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    barracksId = find_building(driver, BuildingType.Barracks)
    if barracksId:
        if enter_building_menu(driver, barracksId):
            status = True
        else:
            logger.error('In function enter_barracks: Failed to enter building')
    else:
        logger.warning('In function enter_barracks: Barracks not found')
    return status


def enter_stable(driver):
    """
    Enters Stable.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    stableId = find_building(driver, BuildingType.Stable)
    if stableId:
        if enter_building_menu(driver, stableId):
            status = True
        else:
            logger.error('In function enter_stable: Failed to enter building')
    else:
        logger.warning('In function enter_stable: Stable not found')
    return status


def enter_siegeworkshop(driver):
    """
    Enters SiegeWorkshop.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    siegeworkshopId = find_building(driver, BuildingType.SiegeWorkshop)
    if siegeworkshopId:
        if enter_building_menu(driver, siegeworkshopId):
            status = True
        else:
            logger.error('In function enter_siegeworkshop: Failed to enter building')
    else:
        logger.warning('In function enter_siegeworkshop: SiegeWorkshop not found')
    return status


def enter_blacksmith(driver):
    """
    Enters Blacksmith.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    blacksmithId = find_building(driver, BuildingType.Blacksmith)
    if blacksmithId:
        if enter_building_menu(driver, blacksmithId):
            status = True
        else:
            logger.error('In function enter_blacksmith: Failed to enter building')
    else:
        logger.warning('In function enter_blacksmith: Blacksmith not found')
    return status


def enter_armoury(driver):
    """
    Enters Armoury.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    armouryId = find_building(driver, BuildingType.Armoury)
    if armouryId:
        if enter_building_menu(driver, armouryId):
            status = True
        else:
            logger.error('In function enter_armoury: Failed to enter building')
    else:
        logger.warning('In function enter_armoury: Armoury not found')
    return status

