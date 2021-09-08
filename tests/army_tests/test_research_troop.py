import time
from Framework.VillageManagement.military.military_utils import enter_academy
from Framework.VillageManagement.military.academy import research
from Framework.utils.Constants import TroopType
from Framework.screen.Login import login


if __name__ == "__main__":
    troop = TroopType.Imperian
    with login(headless=True) as sws:
        if enter_academy(sws):
            research(sws, troop)

