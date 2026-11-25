from app import config


def main():

    if "SFA" in config.UPLAD_UA:
        config.TEMP_DATA.pop("experimental", None)

        try:
            config.TEMP_DATA["route"]["override_android_vpn"] = True
        except (IndexError, KeyError):
            pass

        try:
            inbounds = config.TEMP_DATA["inbounds"]
            inbounds.pop("strict_route", None)
            inbounds.pop("auto_redirect", None)
        except (IndexError, KeyError):
            pass
