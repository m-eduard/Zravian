from Framework.account.Login import login
from selenium.webdriver.support.expected_conditions import staleness_of
from Framework.screen.Views import LevelUpMode, Screens, getTribe, get_current_screen, get_level_up_mode, get_production, get_storage,\
    set_level_up_mode, move_to_overview, move_to_village, move_to_map, move_to_stats


"""
This test checks the view management and logIns.
"""
if __name__ == "__main__":
    with login(headless=False) as sws:
        # Check production
        assert get_production(sws) is not None
        # Check storage
        assert get_storage(sws) is not None
        ### Test move_to functions
        # Test stats
        assert move_to_stats(sws)
        assert get_current_screen(sws) == Screens.STATS
        # Test stats forced
        assert move_to_stats(sws)
        old_elem = sws.getElementAttribute('html', 'text')
        assert get_current_screen(sws) == Screens.STATS
        assert move_to_stats(sws, forced=True)
        assert get_current_screen(sws) == Screens.STATS
        assert staleness_of(old_elem)
        # Test map
        assert move_to_map(sws)
        assert get_current_screen(sws) == Screens.MAP
        # Test map forced
        assert move_to_map(sws)
        old_elem = sws.getElementAttribute('html', 'text')
        assert get_current_screen(sws) == Screens.MAP
        assert move_to_map(sws, forced=True)
        assert get_current_screen(sws) == Screens.MAP
        assert staleness_of(old_elem)
        # Test village
        assert move_to_village(sws)
        assert get_current_screen(sws) == Screens.VILLAGE
        # Test village forced
        assert move_to_village(sws)
        old_elem = sws.getElementAttribute('html', 'text')
        assert get_current_screen(sws) == Screens.VILLAGE
        assert move_to_village(sws, forced=True)
        assert get_current_screen(sws) == Screens.VILLAGE
        assert staleness_of(old_elem)
        # Test overview
        assert move_to_overview(sws)
        assert get_current_screen(sws) == Screens.OVERVIEW
        # Test overview forced
        assert move_to_overview(sws)
        old_elem = sws.getElementAttribute('html', 'text')
        assert get_current_screen(sws) == Screens.OVERVIEW
        assert move_to_overview(sws, forced=True)
        assert get_current_screen(sws) == Screens.OVERVIEW
        assert staleness_of(old_elem)
        ### Check set level up mode functionality
        # Level up mode on
        assert set_level_up_mode(sws, LevelUpMode.ON)
        assert get_level_up_mode(sws) == LevelUpMode.ON
        # Level up mode off
        assert set_level_up_mode(sws, LevelUpMode.OFF)
        assert get_level_up_mode(sws) == LevelUpMode.OFF
