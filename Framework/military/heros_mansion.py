from Framework.infrastructure.builder import check_building_page_title
from Framework.utility.Constants import  BuildingType, TroopType, get_TROOPS, get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr
from selenium.webdriver.common.keys import Keys

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

def name_hero(sws : SWS, newName : str):
    """
    Gives a name to the hero. (should be called after train_hero)

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - newName (str): Denotes hero name.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False

    oldName = sws.getElementAttribute(XPATH.HERO_NAME, Attr.VALUE)
    if oldName:
        for i in range(len(oldName)):
            sws.sendKeys(XPATH.HERO_NAME, Keys.BACKSPACE)

    if sws.sendKeys(XPATH.HERO_NAME, newName):
        logger.success(f'In function name_hero: The hero is named now "{newName}".')
        if sws.clickElement(XPATH.HERO_SAVE_NAME):
            status = True
            logger.success('In function name_hero: The hero name is now saved.')
        else:
            logger.error('In function name_hero: Couldn\'t push save name button.')
    else:
        logger.error('In function name_hero: Couldn\'t send the new hero name in the textbox.')

    return status