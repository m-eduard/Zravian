from Framework.village.builder import level_up_building_at
from Framework.village.builder_utils import ResourceFields, get_building_data
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import get_BUILDINGS
from Framework.screen.Views import get_production
from Framework.account.Login import login


BUILDINGS = get_BUILDINGS()
logger = get_projectLogger()


def raise_lowest_production(sws):
    prod = list(zip(ResourceFields, get_production(sws)))
    prod.sort(key=lambda t: t[1])
    resourceType, _ = prod[0]
    index, level = get_building_data(sws, resourceType)[0]
    assert level_up_building_at(sws, index, forced=True, waitToFinish=True)
    print(f'Leveled {BUILDINGS[resourceType].name} at {index} to level {level + 1}')


def raise_resources_to_level(sws, level):
    while True:
        for resource in ResourceFields:
            if get_building_data(sws, resource)[0][1] < level:
                break
        else:
            break
        raise_lowest_production(sws)
        

"""
This test checks upgrading functions by raising all resource fields to a level.
"""
if __name__ == "__main__":
    logger.set_debugMode(True)
    with login(headless=False) as sws:
        raise_resources_to_level(sws, 20)
