from Framework.military.academy import research
from Framework.utility.Logger import get_projectLogger
from Framework.military.military_utils import enter_academy
from Framework.utility.Constants import Server, TroopType
from Framework.account.Login import login


logger = get_projectLogger()

if __name__ == "__main__":
    logger.set_debugMode(True)
    with login(Server.S10k, username="0bomb8", headless=False) as sws:
        assert enter_academy(sws)
        research(sws, TroopType.Axeman, True)