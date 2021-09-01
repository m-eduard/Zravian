from Framework.utils.Constants import BuildingType, get_BUILDINGS
from Framework.VillageManagement.Builder import construct_building, demolish_building_at, find_building
from Framework.screen.Login import login


BUILDINGS = get_BUILDINGS()


def extract_requirements(bdType, root=True):
    """
    Extracts all requirements for one building.

    Parameters:
        - bdType (BuildingType): Denotes type of building.

    Returns:
        - List of requirements.
    """
    ret = set([bdType])
    for req, _ in BUILDINGS[bdType].requirements:
        ret.update(extract_requirements(req, False))
    if root:
        ret = list(ret)
    return ret


if __name__ == "__main__":
    building = BuildingType.Stable
    with login(headless=False) as driver:
        # Demolish all buildings required for building
        toDemolish = []
        for bd in extract_requirements(building):
            toDemolish += find_building(driver, bd)
        assert(demolish_building_at(driver, toDemolish))
        # Construct building
        assert(construct_building(driver, building, True, True))
        
