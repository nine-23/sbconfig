from app import config


def main():
    if "SFA" in config.UPLAD_UA:
        config.TEMP_DATA.pop("experimental", None)

        try:
            config.TEMP_DATA["route"]["override_android_vpn"] = True
        except (IndexError, KeyError, TypeError):
            pass

        inbounds = config.TEMP_DATA.get("inbounds")
        if isinstance(inbounds, list):
            for inbound in inbounds:
                if isinstance(inbound, dict):
                    inbound.pop("strict_route", None)
                    inbound.pop("auto_redirect", None)
        elif isinstance(inbounds, dict):
            inbounds.pop("strict_route", None)
            inbounds.pop("auto_redirect", None)
