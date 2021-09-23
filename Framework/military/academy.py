from Framework.military.military_utils import enter_academy
from Framework.build.builder import construct_building, level_up_building_at
from Framework.build.builder_utils import check_building_page_title, get_building_data
from Framework.utility.SeleniumUtils import SWS
from Framework.utility.Constants import BuildingType, TroopType, get_TROOPS, get_XPATH
from Framework.utility.Logger import get_projectLogger


logger = get_projectLogger()
TROOPS = get_TROOPS()
XPATH = get_XPATH()


def select_and_research(sws : SWS, tpType : TroopType):
    """
    Researches troup.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - tpType (TroopType): Denotes troop.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if check_building_page_title(sws, BuildingType.Academy):
        if sws.clickElement(XPATH.RESEARCH_TROOP % TROOPS[tpType].name):
            status = True
        else:
            logger.error('In select_and_research: Failed to press upgrade')
    else:
        logger.error('In select_and_research: Not academy view')
    return status


def check_troop_bd_requirements(sws : SWS, tpType : TroopType, forced : bool = False):
    """
    Verifies requirements for troup.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - tpType (TroopType): Denotes troop.
        - forced (bool): If True bypass any inconvenience, False by default.

    Returns:
        - True if the requirements are fulfilled.
    """
    status = False
    requirements = TROOPS[tpType].requirements
    
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
    return status


def research(sws : SWS, tpType : TroopType, forced : bool = False):
    """
    Researches troup.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - tpType (TroopType): Denotes troop.
        - forced (bool): If True bypass any inconvenience, False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if check_troop_bd_requirements(sws, tpType, forced):
        enter_academy(sws)
        if select_and_research(sws, tpType):
            logger.success(f'In function research: {TROOPS[tpType].name} was researched.')
            status = True
        else:
            logger.error('In function research: Failed to research troop.')
    else:
        logger.error('In function research: Failed to check and resolve requirements.')
    return status
    
