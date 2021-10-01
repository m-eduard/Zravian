from enum import Enum
from Framework.screen.General import return_stable
from Framework.screen.Navigation import move_to_plus
from Framework.utility.Constants import get_XPATH, get_projectLogger, time_to_seconds
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


class PlusOptions(Enum):
    ZRAVIAN_PLUS = 'Plus account'
    LUMBER = 'Lumber production'
    CLAY = 'Clay production'
    IRON = 'Iron production'
    CROP = 'Crop production'


def get_gold_amount(sws: SWS):
    """
    Extracts the current gold.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - Int representing gold amount if operation was successful, None otherwise.
    """
    ret = None
    amount = sws.getElementAttribute(XPATH.GOLD_AMOUNT, Attr.TEXT)
    if amount:
        try:
            ret = int(amount)
        except:
            logger.error(f'In get_gold_amount: Invalid amount format: {amount}')
    else:
        logger.error('In get_gold_amount: Failed to extract gold amount')
    return ret


@return_stable
def get_plus_option_cost(sws: SWS, option: PlusOptions):
    """
    Enters ZravianPlus menu and retrieves cost of an option.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - option (PlusOption): Option to activate.

    Returns:
        - Int representing gold cost if operation was successful, None otherwise.
    """
    ret = None
    if move_to_plus(sws):
        cost = sws.getElementsAttribute(XPATH.PLUS_MENU_OPT_COST, Attr.TEXT)
        if cost:
            try:
                ret = int(cost)
            except:
                logger.error(f'In get_plus_option_cost: Invalid cost format: {cost}')
        else:
            logger.error('In get_plus_option_cost: Failed to retrieve cost')
    else:
        logger.error('In get_plus_option_cost: Failed to enter Plus menu')
    return ret


@return_stable
def activate_plus_option(sws: SWS, option: PlusOptions):
    """
    Enters ZravianPlus menu and activates or extends an option.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - option (PlusOption): Option to activate.

    Returns:
        - True if operation was successful, False otherwise.
    """
    ret = False
    if move_to_plus(sws):
        gold = get_gold_amount(sws)
        cost = get_plus_option_cost(sws, option)
        if gold >= cost:
            if sws.isVisible(XPATH.PLUS_MENU_ACTIVATE_OPT % option.value):
                if sws.clickElement(XPATH.PLUS_MENU_ACTIVATE_OPT % option.value, refresh=True):
                    ret = True
                else:
                    logger.error('In activate_plus_option: Failed to click Activate/Extend')
            else:
                logger.error('In activate_plus_option: Activate/Extend not found')
        else:
            logger.warning(f'In activate_plus_option: Not enough gold {gold} < {cost}')
    else:
        logger.error('In activate_plus_option: Failed to enter Plus menu')
    return ret


@return_stable
def get_plus_option_remaining_time(sws: SWS, option: PlusOptions):
    """
    Enters ZravianPlus menu and checks remaining time of an option.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - option (PlusOption): Option to activate.

    Returns:
        - Remianing time in seconds if operation was successful, None otherwise.
    """
    ret = None
    # Zravian event jam text
    ZRAVIAN_EJ_TEXT = '00?'
    if move_to_plus(sws):
        propList = [XPATH.PLUS_MENU_OPT_TIME_LEFT % option.value, XPATH.INSIDE_TIMER]
        if sws.isVisible(propList):
            timer = sws.getElementAttribute(propList, Attr.TEXT)
            if timer:
                if ZRAVIAN_EJ_TEXT in timer:
                    timer = ''.join([char for char in timer if char != '?'])
                    sws.refresh()
                ret = time_to_seconds(timer)
            else:
                logger.error('In get_plus_option_remaining_time: Failed to retrieve remaining time')
        else:
            logger.warning(f'In get_plus_option_remaining_time: {option} not enabled')
    else:
        logger.error('In get_plus_option_remaining_time: Failed to enter Plus menu')
    return ret
