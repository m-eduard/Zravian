from Framework.VillageManagement.Builder import construct_building, level_up_building_at
from Framework.VillageManagement.Utils import check_building_page_title, get_building_data
from Framework.utils.SeleniumUtils import clickElement, isVisible
from Framework.utils.Constants import BuildingType, TroopType, get_TROOPS, get_XPATHS
from Framework.utils.Logger import ProjectLogger


logger = ProjectLogger()
TROOPS = get_TROOPS()
XPATH = get_XPATHS()

def select_and_research(driver, tpType):
    """
    Researches troup.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - tpType (TroopType): Denotes troop.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if isinstance(tpType, TroopType):
        if check_building_page_title(driver, BuildingType.Academy):
            if clickElement(driver, XPATH.RESEARCH_TROOP % TROOPS[tpType].name):
                logger.success(f'In function select_and_research: {TROOPS[tpType].name} was researched')
                status = True
            else:
                logger.error('In function select_and_research: Failed to press upgrade')
        else:
            logger.error('In function select_and_research: Not academy screen')
    else:
        logger.error('In function select_and_research: Invalid parameter tptype')
    return status


def check_troop__bd_requirements(driver, tpType, forced=False):
    """
    Verifies requirements for troup.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - tpType (TroopType): Denotes troop.
        - forced (Boolean): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirements are fulfilled.
    """
    status = False
    if isinstance(tpType, TroopType):
        requirements = TROOPS[type].requirements
        for reqBd, reqLevel in requirements:
            reqBdList = get_building_data(driver, reqBd)
            if not reqBdList:  # Construct
                if forced:
                    if not construct_building(driver, reqBd, forced=True, waitToFinish=True):
                        logger.error(f'In function check_requirements: Failed to construct {reqBd}')
                        break
                else:
                    logger.warning(f'In function check_requirements: {reqBd} not found')
                    break
            reqBdList = get_building_data(driver, reqBd)
            # Check level
            if reqBdList[-1][1] < reqLevel:  # Upgrade is required
                if forced:
                    while reqBdList[-1][1] < reqLevel:
                        if not level_up_building_at(driver, reqBdList[-1][0], forced=True, waitToFinish=True):
                            logger.error(f'In function check_requirements: Failed to level up {reqBd}')
                            break
                        reqBdList = get_building_data(driver, reqBd)
                else:
                    logger.warning(f'In function check_requirements: {reqBd} level is too low')
                    break
        else:  # If not break encountered, all requirements are fulfilled
            status = True
    else:
        logger.error('In function check_requirements: Invalid parameter tpType')
    return status


def research(driver, tpType, forced=False):
    """
    Researches troup.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - tpType (TroopType): Denotes troop.
        - forced (Boolean): If True bypass any inconvenience, False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if isinstance(tpType, TroopType):
        pass
    else:
        logger.error('In function check_requirements: Invalid parameter tpType')
    return status



