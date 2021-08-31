from selenium.webdriver.support.expected_conditions import staleness_of
from Framework.utils.SeleniumUtils import getElementAttribute
from Framework.utils.Constants import get_ACCOUNT
from Framework.utils.Constants import get_ACCOUNT
from Framework.screen.Login import login
from Framework.screen.Views import LevelUpMode, Screens, getTribe, get_current_screen, get_level_up_mode, get_production, get_storage,\
    set_level_up_mode, move_to_overview, move_to_village, move_to_map, move_to_stats


ACCOUNT = get_ACCOUNT()


if __name__ == "__main__":
    with login(headless=False) as driver:
        ### Test visual getters
        # Check tribe
        assert ACCOUNT.TRIBE == getTribe(driver)
        # Check production
        assert get_production(driver) is not None
        # Check storage
        assert get_storage(driver) is not None
        ### Test move_to functions
        # Test stats
        assert move_to_stats(driver)
        assert get_current_screen(driver) == Screens.STATS
        # Test stats forced
        assert move_to_stats(driver)
        old_elem = getElementAttribute(driver, 'html', 'text')
        assert get_current_screen(driver) == Screens.STATS
        assert move_to_stats(driver, forced=True)
        assert get_current_screen(driver) == Screens.STATS
        assert staleness_of(old_elem)
        # Test map
        assert move_to_map(driver)
        assert get_current_screen(driver) == Screens.MAP
        # Test map forced
        assert move_to_map(driver)
        old_elem = getElementAttribute(driver, 'html', 'text')
        assert get_current_screen(driver) == Screens.MAP
        assert move_to_map(driver, forced=True)
        assert get_current_screen(driver) == Screens.MAP
        assert staleness_of(old_elem)
        # Test village
        assert move_to_village(driver)
        assert get_current_screen(driver) == Screens.VILLAGE
        # Test village forced
        assert move_to_village(driver)
        old_elem = getElementAttribute(driver, 'html', 'text')
        assert get_current_screen(driver) == Screens.VILLAGE
        assert move_to_village(driver, forced=True)
        assert get_current_screen(driver) == Screens.VILLAGE
        assert staleness_of(old_elem)
        # Test overview
        assert move_to_overview(driver)
        assert get_current_screen(driver) == Screens.OVERVIEW
        # Test overview forced
        assert move_to_overview(driver)
        old_elem = getElementAttribute(driver, 'html', 'text')
        assert get_current_screen(driver) == Screens.OVERVIEW
        assert move_to_overview(driver, forced=True)
        assert get_current_screen(driver) == Screens.OVERVIEW
        assert staleness_of(old_elem)
        ### Check set level up mode functionality
        # Level up mode on
        assert set_level_up_mode(driver, LevelUpMode.ON)
        assert get_level_up_mode(driver) == LevelUpMode.ON
        # Level up mode off
        assert set_level_up_mode(driver, LevelUpMode.OFF)
        assert get_level_up_mode(driver) == LevelUpMode.OFF
