from app.main import genconfig, outbound, ua
from app import config


def main(input_temp: str = ""):

    target_temp = input_temp.strip() if input_temp else str(config.DEFAULT_TEMP)

    if input_temp != config.DEFAULT_TEMP.name:
        config.TEMP_OK = outbound.main(target_temp)

    ua.main()

    genconfig.main()
