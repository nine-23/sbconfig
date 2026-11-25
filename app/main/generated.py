from app.main import genconfig, outbound, ua


def main(input_temp: str = ""):
    cleaned_temp = input_temp.strip()
    outbound.main(cleaned_temp)
    ua.main()
    genconfig.main()
