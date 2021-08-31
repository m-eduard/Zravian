from Framework.utils.Constants import get_BUILDINGS


def time_to_seconds(currTime):
    """
    Converts time in format hh:mm:ss to seconds
    :param currTime: time in format hh:mm:ss.
    :return: equivalent time in seconds.
    """
    h, m, s = currTime.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def find_building_by_name(name):
    """
    Finds a building type by its name.
    :param name: String.
    :return: BuildingType or None.
    """
    buildings = get_BUILDINGS()
    for _, building in buildings.items():
        if building.name in name:
            return building
    return None
