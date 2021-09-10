from Framework.account.Login import login
from Framework.utility.Constants import BuildingType, get_BUILDINGS
from Framework.village.builder import find_building

BUILDINGS = get_BUILDINGS()


if __name__ == "__main__":
    with login(headless=True) as sws:
        # Requires manual checking
        for bdType in BuildingType:
            if bdType != BuildingType.EmptyPlace:
                print(f'{BUILDINGS[bdType].name}: {find_building(sws, bdType)}')
