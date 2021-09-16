from Framework.village.builder_utils import check_building_page_title
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import  BuildingType, TroopType, get_TROOPS, get_XPATH
from Framework.utility.SeleniumUtils import SWS


logger = get_projectLogger()
TROOPS = get_TROOPS()
XPATH = get_XPATH()

def make_troops_by_amount(sws : SWS, tpType : TroopType, amount : int):
    """
    Trains Troops by specified type and amount.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - tpType (TroopType): Denotes troop.
        - amount: Denotes the amount of troops to be trained.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    status = False
    if check_building_page_title(sws, BuildingType.Barracks):
        #de modificat acilisea
        text = sws.getElementAttribute(XPATH.TROOP_MAX_UNITS % TROOPS[tpType].name, 'text')[0]
        text = text[1:-1]
        if int(text) > amount:
            if sws.sendKeys(XPATH.TROOP_INPUT_BOX % TROOPS[tpType].name, amount):
                if sws.clickElement(XPATH.TROOP_TRAIN_BTN, refresh=True):
                    logger.success(f'In function make_troops_by_amount: {amount} {TROOPS[tpType].name} were trained')
                    status = True
                else:
                    logger.error('In function make_troops_by_amount: Failed to press train')
            else:
                logger.error('In function make_troops_by_amount: Failed to insert amount of troops')
        else:
            logger.warning('In function make_troops_by_amount: Not enough resources')
    else:
        logger.error('In function make_troops_by_amount: Not barracks screen')

    return status

    