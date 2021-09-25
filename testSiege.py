from re import M
from Framework.infrastructure.builder import enter_building
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import Server, TroopType, BuildingType
from Framework.account.Login import login
from Framework.military.siege import make_siege_troops_by_amount, get_siege_total_training_time
from Framework.military.troops_trainer import get_total_training_time, make_troops_by_amount

logger = get_projectLogger()

if __name__ == "__main__":
    logger.set_debugMode(True)
    with login(Server.S10k, username="0bomb8", headless=False) as sws:
        #assert enter_building(sws, BuildingType.SiegeWorkshop)
        make_troops_by_amount(sws, TroopType.RRam, 500)
        get_total_training_time(sws)
        make_troops_by_amount(sws, TroopType.Paladin, 100)
        make_troops_by_amount(sws, TroopType.Scout, 100)
        