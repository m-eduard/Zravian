import pytest
import sys
import os

# Path to root
sys.path.append(os.path.join(sys.path[0], '../'))

from Framework.account.Login import Login
from Framework.utility.SeleniumWebScraper import SWS
from Framework.infrastructure.builder import BuildingError, RESOURCE_FIELDS, construct_building, demolish_building_at, find_building, \
    level_up_building_at
from Framework.infrastructure.buildings import get_village_data
from Framework.utility.Constants import BuildingType, Server


def demolish_everything(sws : SWS):
    """Demolishes everything in village except MainBuilding, Wall if its built and Resource Fields."""
    to_demolish = []
    ignored_buildings = [BuildingType.EmptyPlace, *RESOURCE_FIELDS, BuildingType.MainBuilding, BuildingType.Wall]
    for site in [siteId for bd, lst in get_village_data(sws).items() if bd not in ignored_buildings and lst for \
            (siteId, _) in lst]:
        to_demolish.append(site)
    return demolish_building_at(sws, to_demolish)


def check_buildings_to_be(sws : SWS, expected : list):
    """Checks for only the expected buildings to be in the village."""
    expected = list(set([*expected, BuildingType.EmptyPlace, *RESOURCE_FIELDS]))
    return sorted([bd for bd, lst in get_village_data(sws).items() if lst]) == sorted(expected)


# Testing constants
HEADLESS = True
USERNAME = '0bomb1'


class Test_02_builder_smokeTest:
    def test_02_builder_smokeTest_01(self):
        """
        This test case checks constrcution of trivial buildings, leveling up of buildings,
        demolishing buildings and handling of building problems (requirements not fulfilled,
        busy workers, attempting to level up a maxed building).
        Steps:
            1. If not constructed, construct Main Building and Wall.
            2. Level MainBuilding to at least level 10.
            3. Demolish every building besides MainBuilding.
            4. Construct all no requirements buildings.
            5. Max level cranny.
            6. Attempt to level it up again.
            7. Attempt to build another Cranny.
            8. Demolish every building besides MainBuilding.
            9. Construct Stables.
            10. Demolish every building besides MainBuilding.
            11. Construct Town Hall.
            12. Demolish every building besides MainBuilding.
            13. Construct Residence.
            14. Demolish every building besides MainBuilding.
            15. Construct Palace.
            16. Demolish every building besides MainBuilding.
            17. Construct Siege Workshop.
            18. Demolish every building besides MainBuilding.
            19. Level up wall to level 5.
        Objectives:
            1. Main Building and Wall should be constructed.
            2. Main Building should be at least level 10.
            3. Only Main Building in village.
            4. Only buildings in village:
                - Woodcutter
                - Clay Pit
                - Iron Mine
                - Cropland
                - Main Building
                - Rally Point
                - Wall
                - Cranny
            6. Level up should fail.
            7. Construction should succeed.
            8. Only Main Building and Wall in the village.
            9. Stables constructed alongside Academy, Blacksmith, Barracks, Rally Point.
            10. Only Main Building and Wall in the village.
            11. Town Hall constructed alongside Academy, Barracks, Rally Point.
            12. Only Main Building and Wall in the village.
            13. Residence constructed.
            14. Only Main Building and Wall in the village.
            15. Palace constructed alongside Embassy.
            16. Only Main Building and Wall in the village.
            17. Siege Workshop constructed alongside Academy, Barracks, Rally Point.
            18. Only Main Building and Wall in the village.
            19. Wall at level 5.
        """
        # Main building level
        MB_LEVEL = 10
        # Cranny max level
        CRANNY_MAX_LEVEL = 10
        # Wall to level 5
        WALL_LEVEL = 5
        # Buildings in village after everything else is demolished
        with Login(Server.S10k, USERNAME, headless=False) as sws:
            # S1. If not constructed, construct Main Building and Wall.
            # O1. Main Building and Wall should be constructed.
            construct_building(sws, BuildingType.MainBuilding, True, True)
            construct_building(sws, BuildingType.Wall, True, True)
            mb_id = find_building(sws, BuildingType.MainBuilding).siteId
            wall_id = find_building(sws, BuildingType.Wall).siteId
            assert mb_id is not None and wall_id is not None

            # S2. Level MainBuilding to at least level 10.
            while find_building(sws, BuildingType.MainBuilding).level < MB_LEVEL:
                assert level_up_building_at(sws, mb_id, True, True) == BuildingError.OK
            # O2. Main Building should be at least level 10.
            try:
                find_building(sws, BuildingType.MainBuilding).level >= MB_LEVEL
            except AttributeError:
                raise AssertionError

            # S3. Demolish every building besides MainBuilding.
            assert demolish_everything(sws)
            # O3. Only Main Building in village.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])

            # S4. Construct all no requirements buildings.
            expected_buildings = [BuildingType.MainBuilding, BuildingType.RallyPoint, BuildingType.Wall, \
                BuildingType.Cranny]
            for bd in expected_buildings:
                construct_building(sws, bd, True, True)
            # O4. Only buildings in village:
            # - Main Building
            # - Rally Point
            # - Wall
            # - Cranny
            assert check_buildings_to_be(sws, expected_buildings)

            # S5. Max level cranny.
            cranny_index = find_building(sws, BuildingType.Cranny).siteId
            while find_building(sws, BuildingType.Cranny).level < CRANNY_MAX_LEVEL:
                assert level_up_building_at(sws, cranny_index, True, True) == BuildingError.OK

            # S6. Attempt to level it up again.
            # O6. Level up should fail.
            assert level_up_building_at(sws, cranny_index, True, True) == BuildingError.MAX_LEVEL_ALREADY

            # S7. Attempt to build another Cranny.
            # O7. Construction should succeed.
            assert construct_building(sws, BuildingType.Cranny, True, True) == BuildingError.OK

            # S8. Demolish every building besides MainBuilding.
            assert demolish_everything(sws)
            # O8. Only Main Building and Wall in the village.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])

            # S9. Construct Stables.
            assert construct_building(sws, BuildingType.Stable, True, True) == BuildingError.OK
            # O9. Stables constructed alongside Academy, Blacksmith, Barracks, Rally Point.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall, BuildingType.Stable, \
                BuildingType.Academy, BuildingType.Blacksmith, BuildingType.Barracks, BuildingType.RallyPoint])

            # S10. Demolish every building besides MainBuilding.
            assert demolish_everything(sws)
            # O10. Only Main Building and Wall in the village.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])

            # S11. Construct Town Hall.
            assert construct_building(sws, BuildingType.TownHall, True, True) == BuildingError.OK
            # O11. Town Hall constructed alongside Academy, Barracks, Rally Point.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall, \
                BuildingType.TownHall, BuildingType.Academy, BuildingType.Barracks, BuildingType.RallyPoint, \
                BuildingType.Warehouse])
            
            # S12. Demolish every building besides MainBuilding.
            assert demolish_everything(sws)
            # O12. Only Main Building and Wall in the village.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])

            # S13. Construct Residence.
            assert construct_building(sws, BuildingType.Residence, True, True) == BuildingError.OK
            # O13. Residence constructed.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall, \
                BuildingType.Residence])

            # S14. Demolish every building besides MainBuilding.
            assert demolish_everything(sws)
            # O14. Only Main Building and Wall in the village.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])

            # S15. Construct Palace.
            assert construct_building(sws, BuildingType.Palace, True, True) == BuildingError.OK
            # O15. Palace constructed alongside Embassy.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall, BuildingType.Palace, \
                BuildingType.Embassy])

            # S16. Demolish every building besides MainBuilding.
            assert demolish_everything(sws)
            # O16. Only Main Building and Wall in the village.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])

            # S17. Construct Siege Workshop.
            assert construct_building(sws, BuildingType.SiegeWorkshop, True, True) == BuildingError.OK
            # O17. Siege Workshop constructed alongside Academy, Barracks, Rally Point.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall, \
                BuildingType.SiegeWorkshop, BuildingType.Academy, BuildingType.Barracks, BuildingType.RallyPoint, \
                BuildingType.Warehouse])

            # S18. Demolish every building besides MainBuilding.
            assert demolish_everything(sws)
            # O18. Only Main Building and Wall in the village.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])

            # S19. Level up wall to level 5.
            # O19. Wall at level 5.
            wall_id = find_building(sws, BuildingType.Wall).siteId
            while find_building(sws, BuildingType.Wall).level < WALL_LEVEL:
                assert level_up_building_at(sws, wall_id, True, True) == BuildingError.OK

    def test_02_builder_smokeTest_02(self):
        """
        This test case is a stress test used to spot sporadically appearing
        problems by repeating complex actions for a number of times.
        Steps:
            1. If not constructed, construct Main Building and Wall.
            2. Level MainBuilding to at least level 10.
            3. Demolish every building besides MainBuilding.
            4. Repeat the steps 5 to 8 for 3 times.
            5. Construct Stables.
            6. Demolish every building besides MainBuilding.
            7. Construct Town Hall.
            8. Demolish every building besides MainBuilding.
        Objectives:
            1. Main Building and Wall should be constructed.
            2. Main Building should be at least level 10.
            3. Only Main Building in village.
            4. Logs should not contain any error message.
            5. Stables constructed alongside Academy, Blacksmith, Barracks, Rally Point.
            6. Only Main Building and Wall in the village.
            7. Town Hall constructed alongside Academy, Barracks, Rally Point.
            8. Only Main Building and Wall in the village.
        """
        # Main building level
        MB_LEVEL = 10
        # Stress test number of iterations
        STRESS_COUNT = 3
        # Buildings in village after everything else is demolished
        with Login(Server.S10k, USERNAME, headless=False) as sws:
            # S1. If not constructed, construct Main Building and Wall.
            # O1. Main Building and Wall should be constructed.
            construct_building(sws, BuildingType.MainBuilding, True, True)
            construct_building(sws, BuildingType.Wall, True, True)
            mb_id = find_building(sws, BuildingType.MainBuilding).siteId
            wall_id = find_building(sws, BuildingType.Wall).siteId
            assert mb_id is not None and wall_id is not None

            # S2. Level MainBuilding to at least level 10.
            while find_building(sws, BuildingType.MainBuilding).level < MB_LEVEL:
                assert level_up_building_at(sws, mb_id, True, True) == BuildingError.OK
            # O2. Main Building should be at least level 10.
            try:
                find_building(sws, BuildingType.MainBuilding).level >= MB_LEVEL
            except AttributeError:
                raise AssertionError

            # S3. Demolish every building besides MainBuilding.
            assert demolish_everything(sws)
            # O3. Only Main Building in village.
            assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])

            # S4. Repeat steps 4 to 7 for 10 times.
            # O4. Logs should not contain any error message.
            for _ in range(STRESS_COUNT):
                # S5. Construct Stables.
                assert construct_building(sws, BuildingType.Stable, True, True) == BuildingError.OK
                # O5. Stables constructed alongside Academy, Blacksmith, Barracks, Rally Point.
                assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall, \
                    BuildingType.Stable, BuildingType.Academy, BuildingType.Blacksmith, BuildingType.Barracks, \
                    BuildingType.RallyPoint])

                # S6. Demolish every building besides MainBuilding.
                assert demolish_everything(sws)
                # O6. Only Main Building and Wall in the village.
                assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])

                # S7. Construct Town Hall.
                assert construct_building(sws, BuildingType.TownHall, True, True) == BuildingError.OK
                # O7. Town Hall constructed alongside Academy, Barracks, Rally Point.
                assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall, \
                    BuildingType.TownHall, BuildingType.Academy, BuildingType.Barracks, BuildingType.RallyPoint, \
                    BuildingType.Warehouse])

                # S8. Demolish every building besides MainBuilding.
                assert demolish_everything(sws)
                # O8. Only Main Building and Wall in the village.
                assert check_buildings_to_be(sws, [BuildingType.MainBuilding, BuildingType.Wall])
