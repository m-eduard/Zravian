from enum import IntEnum, Enum
from Framework.utility.Constants import Tribe, get_XPATH
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS


logger = get_projectLogger()
XPATH = get_XPATH()
TRIBE = None



class Views(Enum):
    OVERVIEW = 'village1.php'
    VILLAGE = 'village2.php'
    MAP = 'map.php'
    STATS = 'statistics.php'
    PROFILE = 'profile.php'


def get_current_view(sws : SWS):
    """
    Tells which of the following view is active:
      - Overview
      - Village
      - Map
      - Statistics
      - None, if you are inside a menu i.e. Constructing a new building.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - Current view if operation was successful, None otherwise.
    """
    for view in Views:
        if view.value in sws.getCurrentUrl():
            return view
    return None


def __move_to_view(sws : SWS, view : Views, forced : bool = False):
    """
    Ensures that the current view is the desired view.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - view (Views): Desired view.
        - forced (bool): If True will refresh the view even tho
            is the desired one, False by default

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    BASE_URL = sws.getCurrentUrl().rsplit("/", 1)[0] + '/'
    if view != get_current_view(sws) or forced:
        if sws.get(BASE_URL + view.value):
            ret = True
        else:
            logger.error('In __move_to_view: Failed to move to view')
    else:
        ret = True
    return ret


def move_to_overview(sws : SWS, forced : bool = False):
    """
    Changes current view to overview.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_view(sws, Views.OVERVIEW, forced)


def move_to_village(sws : SWS, forced : bool = False):
    """
    Changes current view to village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_view(sws, Views.VILLAGE, forced)


def move_to_map(sws : SWS, forced : bool = False):
    """
    Changes current view to map.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_view(sws, Views.MAP, forced)


def move_to_stats(sws : SWS, forced : bool = False):
    """
    Changes current view to stats.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_view(sws, Views.STATS, forced)


def move_to_profile(sws : SWS, forced : bool = False):
    """
    Changes current view to stats.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_view(sws, Views.PROFILE, forced)
