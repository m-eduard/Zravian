from Framework.account.Login import login
from Framework.utility.Constants import BuildingType, get_BUILDINGS
from Framework.village.builder import get_building_data

BUILDINGS = get_BUILDINGS()


if __name__ == "__main__":
    with login(headless=True) as sws:
        # Requires manual checking
        for bdType in BuildingType:
            if bdType != BuildingType.EmptyPlace:
                data = get_building_data(sws, bdType)
                data = [f'(Index: {d[0]}, Level: {d[1]})' for d in data]
                print(f'{BUILDINGS[bdType].name}: {data}')

