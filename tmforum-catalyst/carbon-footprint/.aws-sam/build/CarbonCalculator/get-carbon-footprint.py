def lambda_handler(event, context):
    OfferName = event["OfferName"]
    if OfferName == "Modem WiFi Premium":
        return {
            "OfferName": OfferName,
            "CO2eOneTime": 111,
            "CO2eMonthly": 80
        }
    elif OfferName == "eMTA 4 Port with WiFi up to 100":
        return {
            "OfferName": OfferName,
            "CO2eOneTime": 79,
            "CO2eMonthly": 50
        }
    elif OfferName == "eMTA 4 Port with WiFi up to 200":
        return {
            "OfferName": OfferName,
            "CO2eOneTime": 89,
            "CO2eMonthly": 60
        }
    elif OfferName == "Suite - eMTA 4 Port with WiFi up to 300 Premium":
        return {
            "OfferName": OfferName,
            "CO2eOneTime": 69,
            "CO2eMonthly": 40
        }
    else:
        return {
            "OfferName": OfferName,
            "CO2eOneTime": 1000,
            "CO2eMonthly": 900
        }