from Framework.screen.Views import get_production
from Framework.VillageManagement.Utils import ResourceFields, get_building_data
from Framework.screen.Login import login
from Framework.VillageManagement.Builder import level_up_building_at


def raise_lowest_production(driver):
    prod = list(zip(ResourceFields, get_production(driver)))
    prod.sort(key=lambda t: t[1])
    resourceType = prod[0][0]
    index = get_building_data(driver, resourceType)[0][0]
    if not level_up_building_at(driver, index, forced=True, waitToFinish=True):
        raise IndexError


def raise_resources_to_level(driver, level):
    while True:
        for resource in ResourceFields:
            if get_building_data(driver, resource)[0][1] < level:
                break
        else:
            break
        raise_lowest_production(driver)
        

if __name__ == "__main__":
    with login(headless=False) as driver:
        raise_resources_to_level(driver, 5)
