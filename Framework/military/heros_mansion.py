from Framework.village.builder_utils import check_building_page_title
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import  BuildingType, TroopType, get_TROOPS, get_XPATH
from Framework.utility.SeleniumUtils import SWS

logger = get_projectLogger()
TROOPS = get_TROOPS()
XPATH = get_XPATH()

def train_hero(sws : SWS, tpType : TroopType):
    """
    Trains a hero.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - tpType (TroopType): Denotes troop.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if check_building_page_title(sws, BuildingType.HeroMansion):
        if not sws.isVisible(XPATH.HERO_EXISTING):
            if sws.clickElement(XPATH.HERO_TRAIN_BTN % TROOPS[tpType].name, refresh=True):
                logger.success(f'In function train_hero: The {TROOPS[tpType].name} hero was trained.')
                status = True
            else:
                logger.error('In function train_hero: Failed to press train')
        else:
            logger.warning("In function train_hero: Can't train another hero as there is already one existing.")
    else:
        logger.error("In function train_hero: Not Hero's Mansion screen")
    
    return status