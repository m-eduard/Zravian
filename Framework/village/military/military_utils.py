from Framework.utils.SeleniumUtils import SWS
from Framework.utils.Constants import BuildingType
from Framework.VillageManagement.Utils import enter_building_menu, find_building
from Framework.utils.Logger import get_projectLogger


logger = get_projectLogger()


# Entering functions
def enter_academy(sws : SWS):
    """
    Enters Academy.

    Parameters:
        - sws (SWS): Selenium Web Scraper

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    academyId = find_building(sws, BuildingType.Academy)
    if academyId:
        if enter_building_menu(sws, academyId):
            status = True
        else:
            logger.error('In enter_academy: Failed to enter building')
    else:
        logger.warning('In enter_academy: Academy not found')
    return status


def enter_barracks(sws : SWS):
    """
    Enters Barracks.

    Parameters:
        - sws (SWS): Selenium Web Scraper

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    barracksId = find_building(sws, BuildingType.Barracks)
    if barracksId:
        if enter_building_menu(sws, barracksId):
            status = True
        else:
            logger.error('In enter_barracks: Failed to enter building')
    else:
        logger.warning('In enter_barracks: Barracks not found')
    return status


def enter_stable(sws : SWS):
    """
    Enters Stable.

    Parameters:
        - sws (SWS): Selenium Web Scraper

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    stableId = find_building(sws, BuildingType.Stable)
    if stableId:
        if enter_building_menu(sws, stableId):
            status = True
        else:
            logger.error('In enter_stable: Failed to enter building')
    else:
        logger.warning('In enter_stable: Stable not found')
    return status


def enter_siegeworkshop(sws : SWS):
    """
    Enters SiegeWorkshop.

    Parameters:
        - sws (SWS): Selenium Web Scraper

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    siegeworkshopId = find_building(sws, BuildingType.SiegeWorkshop)
    if siegeworkshopId:
        if enter_building_menu(sws, siegeworkshopId):
            status = True
        else:
            logger.error('In enter_siegeworkshop: Failed to enter building')
    else:
        logger.warning('In enter_siegeworkshop: SiegeWorkshop not found')
    return status


def enter_blacksmith(sws : SWS):
    """
    Enters Blacksmith.

    Parameters:
        - sws (SWS): Selenium Web Scraper

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    blacksmithId = find_building(sws, BuildingType.Blacksmith)
    if blacksmithId:
        if enter_building_menu(sws, blacksmithId):
            status = True
        else:
            logger.error('In enter_blacksmith: Failed to enter building')
    else:
        logger.warning('In enter_blacksmith: Blacksmith not found')
    return status


def enter_armoury(sws : SWS):
    """
    Enters Armoury.

    Parameters:
        - sws (SWS): Selenium Web Scraper

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    armouryId = find_building(sws, BuildingType.Armoury)
    if armouryId:
        if enter_building_menu(sws, armouryId):
            status = True
        else:
            logger.error('In enter_armoury: Failed to enter building')
    else:
        logger.warning('In enter_armoury: Armoury not found')
    return status

