from Framework.screen.Login import login
from Framework.utils.Constants import BuildingType, get_BUILDINGS
from Framework.VillageManagement.Builder import get_building_data

BUILDINGS = get_BUILDINGS()


if __name__ == "__main__":
    with login(headless=True) as driver:
        # Requires manual checking
        for bdType in BuildingType:
            if bdType != BuildingType.EmptyPlace:
                data = get_building_data(driver, bdType)
                data = [f'(Index: {d[0]}, Level: {d[1]})' for d in data]
                print(f'{BUILDINGS[bdType].name}: {data}')
