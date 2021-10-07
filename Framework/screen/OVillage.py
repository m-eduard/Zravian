from Framework.screen.Navigation import move_to_overview
from Framework.utility.Constants import ResourceType, get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def get_village_name(sws: SWS):
    """
    Gets village name in overview or village screen.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - String with village name if operation was successful, None otherwise.
    """
    ret = None
    if move_to_overview(sws):
        villageName = sws.getElementAttribute(XPATH.VILLAGE_NAME, Attr.TEXT)
        if villageName:
            ret = villageName
        else:
            logger.error('In get_village_name: Failed to extract the village name')
    else:
        logger.warning('In get_village_name: move_to_overview() failed')
    return ret


def get_storage(sws: SWS):
    """
    Gets for storage for each resource for current village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
    
    Returns:
        - Dictionary mapping each resource field to tuple.
    """
    storage = {}
    # Extract lumber storage
    lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, Attr.TEXT)
    if lumber:
        try:
            lumber_curr = int(lumber.split('/')[0])
            lumber_cap = int(lumber.split('/')[1])
            storage[ResourceType.LUMBER] = (lumber_curr, lumber_cap)
        except (IndexError, ValueError) as err:
            logger.error('In get_storage: Lumber storage does not respect pattern. Error: %s' % err)
    else:
        logger.error('In get_storage: Failed to get storage for lumber')
    # Extract clay storage
    clay = sws.getElementAttribute(XPATH.PRODUCTION_CLAY, Attr.TEXT)
    if clay:
        try:
            clay_curr = int(clay.split('/')[0])
            clay_cap = int(clay.split('/')[1])
            storage[ResourceType.CLAY] = (clay_curr, clay_cap)
        except (IndexError, ValueError) as err:
            logger.error('In get_storage: Clay storage does not respect pattern. Error: %s' % err)
    else:
        logger.error('In get_storage: Failed to get storage for clay')
    # Extract iron storage
    iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, Attr.TEXT)
    if iron:
        try:
            iron_curr = int(iron.split('/')[0])
            iron_cap = int(iron.split('/')[1])
            storage[ResourceType.IRON] = (iron_curr, iron_cap)
        except (IndexError, ValueError) as err:
            logger.error('In get_storage: Iron storage does not respect pattern. Error: %s' % err)
    else:
        logger.error('In get_storage: Failed to get storage for iron')
    # Extract crop storage
    crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, Attr.TEXT)
    if crop:
        try:
            crop_curr = int(crop.split('/')[0])
            crop_cap = int(crop.split('/')[1])
            storage[ResourceType.CROP] = (crop_curr, crop_cap)
        except (IndexError, ValueError) as err:
            logger.error('In get_storage: Crop storage does not respect pattern. Error: %s' % err)
    else:
        logger.error('In get_storage: Failed to get storage for crop')
    return storage


def get_production(sws: SWS):
    """
    Gets for production for each resource for current village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
    
    Returns:
        - Dictionary mapping each resource to its production value.
    """
    production = {}
    # Extract lumber production
    lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, Attr.TITLE)
    if lumber:
        try:
            production[ResourceType.LUMBER] = int(lumber)
        except ValueError as err:
            logger.error('In get_production: Failed to convert to int. Error: %s' % err)
    else:
        logger.error('In get_production: Failed to get production for lumber')
    # Extract clay production
    clay = sws.getElementAttribute(XPATH.PRODUCTION_CLAY, Attr.TITLE)
    if clay:
        try:
            production[ResourceType.CLAY] = int(clay)
        except ValueError as err:
            logger.error('In get_production: Failed to convert to int. Error: %s' % err)
    else:
        logger.error('In get_production: Failed to get production for clay')
    # Extract iron production
    iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, Attr.TITLE)
    if iron:
        try:
            production[ResourceType.IRON] = int(iron)
        except ValueError as err:
            logger.error('In get_production: Failed to convert to int. Error: %s' % err)
    else:
        logger.error('In get_production: Failed to get production for iron')
    # Extract crop production
    crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, Attr.TITLE)
    if crop:
        try:
            production[ResourceType.CROP] = int(crop)
        except ValueError as err:
            logger.error('In get_production: Failed to convert to int. Error: %s' % err)
    else:
        logger.error('In get_production: Failed to get production for crop')
    return production
