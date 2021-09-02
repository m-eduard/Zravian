

from Framework.utils.Constants import BuildingType
from Framework.VillageManagement.Utils import find_building


def enter_academy(driver):
    """
    Enters Academy.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    academyIds = find_building(driver, BuildingType.Academy)
    if academyIds:
        academyId = academyIds[0]

