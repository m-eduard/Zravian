import re
import Framework.screen.Navigation as NAV
from Framework.utility.Constants import Building, BuildingType, get_XPATH, get_building_info, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()
# List of all resource buildings
RESOURCE_FIELDS = [BuildingType.Woodcutter, BuildingType.ClayPit, BuildingType.IronMine, BuildingType.Cropland]
# First building site from village
FIRST_BUILDING_SITE_VILLAGE = 19
# Last building site from village
LAST_BUILDING_SITE_VILLAGE = 40


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
    if bdType in RESOURCE_FIELDS:
        moveStatus = NAV.move_to_overview(sws)
    else:
        moveStatus = NAV.move_to_village(sws)
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
            # Sort ascending by building level and descending by siteId
            lst.sort(key=lambda e: (int(e[1]), -int(e[0])))
            ret = lst
    else:
        logger.error('In get_buildings: move_to_screen() failed')
    return ret


def get_village_data(sws: SWS):
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
    for bdType in RESOURCE_FIELDS:
        buildingsDict[bdType] = get_buildings(sws, bdType)
        if buildingsDict[bdType] is None:
            break
    else:
        # Get all buildings
        for bdType in BuildingType:
            if bdType in RESOURCE_FIELDS:
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
