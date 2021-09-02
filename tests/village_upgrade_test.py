from Framework.utils.Constants import get_BUILDINGS
from Framework.screen.Views import get_production
from Framework.screen.Login import login
from Framework.VillageManagement.Utils import ResourceFields, get_building_data
from Framework.VillageManagement.Builder import BUILDINGS, level_up_building_at


BUILDINGS = get_BUILDINGS()


def raise_lowest_production(driver):
    prod = list(zip(ResourceFields, get_production(driver)))
    prod.sort(key=lambda t: t[1])
    resourceType, _ = prod[0]
    index, level = get_building_data(driver, resourceType)[0]
    assert level_up_building_at(driver, index, forced=True, waitToFinish=True)
    print(f'Leveled {BUILDINGS[resourceType].name} at {index} to level {level + 1}')


def raise_resources_to_level(driver, level):
    while True:
        for resource in ResourceFields:
            if get_building_data(driver, resource)[0][1] < level:
                break
        else:
            break
        raise_lowest_production(driver)
        

"""
This test checks upgrading functions by raising all resource fields to a level.
"""
if __name__ == "__main__":
    with login(headless=False) as driver:
        raise_resources_to_level(driver, 20)
