#!/usr/bin/env python
"""Get air quality data for specific location."""
import argparse
import json
import urllib.request


def get_class(aqi: int):
    """Return CSS class for Waybar widget."""
    cssclass = ""
    if aqi <= 50:
        cssclass = "good"
    elif aqi <= 100:
        cssclass = "moderate"
    elif aqi <= 150:
        cssclass = "sensitive"
    elif aqi <= 200:
        cssclass = "unhealthy"
    elif aqi <= 300:
        cssclass = "veryUnhealthy"
    else:
        cssclass = "hazardous"
    return cssclass


def get_details(data: dict):
    """Add missing details for tooltip."""
    details = ""
    texts = dict(
        pm25="Fine particulate matter (PM₂.₅)      : {:4.1f} ({})",
        pm10="Respirable particulate matter (PM₁₀) : {:4.1f} ({})",
        o3="Ozone (O₃)                           : {:4.1f} ({})",
        no2="Nitrogen dioxide (NO₂)               : {:4.1f} ({})",
        so2="Sulfur dioxide (SO₂)                 : {:4.1f} ({})",
        co="Carbon monoxide (CO)                 : {:4.1f} ({})")

    vals = dict()
    missing = list()
    values = ["pm25", "pm10", "o3", "no2", "so2", "co"]
    for value in values:
        try:
            vals[value] = float(data[value]["v"])
        except KeyError as error:
            missing.append(error.args[0])

    for value in values:
        if not (value in missing):
            if len(details) > 0:
                details += "\n"
            details += texts[value].format(vals[value], get_level(vals[value]))
    return details


def get_tooltip(data: dict):
    """Generate tooltip data for widget."""
    tooltip = "<b>Station:</b> " + str(data["city"]["name"]) + "\n\n"

    aqi = int(data["aqi"])
    if aqi <= 50:
        tooltip += "<b>Pollution level: <i>Good</i></b>   ({})\n\n"\
            "Air quality is considered satisfactory, and air pollution poses "\
            "little or no risk.".format(aqi)
    elif aqi <= 100:
        tooltip += "<b>Pollution level: <i>Moderate</i></b>   ({})\n\n"\
            "Air quality is acceptable; however, for some pollutants there "\
            "may be a moderate health concern for a very small number of "\
            "people who are unusually sensitive to air pollution.\n\n"\
            "Active children and adults, and people with respiratory "\
            "disease, such as asthma, should limit prolonged outdoor "\
            "exertion.".format(aqi)
    elif aqi <= 150:
        tooltip += "<b>Pollution level: <i>Unhealthy for sensitive "\
            "groups</i></b>   ({})\n\n"\
            "Members of sensitive groups may experience health effects. "\
            "The general public is not likely to be affected.\n\n"\
            "Active children and adults, and people with respiratory "\
            "disease, such as asthma, should limit prolonged outdoor "\
            "exertion.".format(aqi)
    elif aqi <= 200:
        tooltip += "<b>Pollution level: <i>Unhealthy</i></b>   ({})\n\n"\
            "Everyone may begin to experience health effects; members of "\
            "sensitive groups may experience more serious health effects.\n\n"\
            "Active children and adults, and people with respiratory "\
            "disease, such as asthma, should avoid prolonged outdoor "\
            "exertion; everyone else, especially children, should limit "\
            "prolonged outdoor exertion.".format(aqi)
    elif aqi <= 300:
        tooltip += "<b>Pollution level: <i>Very unhealthy</i></b>   ({})"\
            "Health warnings of emergency conditions. The entire population "\
            "is more likely to be affected.\n\n"\
            "Active children and adults, and people with respiratory disease,"\
            " such as asthma, should avoid all outdoor exertion; everyone "\
            "else, especially children, should limit outdoor "\
            "exertion.".format(aqi)
    else:
        tooltip += "<b>Pollution level: <i>Hazardous</i></b>   ({})\n\n"\
            "Health alert: Everyone may experience more serious health "\
            "effects.\n\n"\
            "Everyone should avoid all outdoor exertion.".format(aqi)

    details = get_details(data["iaqi"])
    if len(details) > 0:
        tooltip += "\n\n<b>Details per pollutant (AQI levels):</b>\n\n" + \
            "<small><tt>" + details + "</tt></small>"

    return tooltip


def get_level(aqi: int):
    """Get AQI level for location."""
    if aqi <= 50:
        level = "Good"
    elif aqi <= 100:
        level = "Moderate"
    elif aqi <= 150:
        level = "Unhealthy for sensitive groups"
    elif aqi <= 200:
        level = "Unhealthy"
    elif aqi <= 300:
        level = "Very unhealthy"
    else:
        level = "Hazardous"
    return level


parser = argparse.ArgumentParser(prog="info-aqi",
                                 description=("Get Air quality information of a specific location"))
parser.add_argument("-l", "--location",
                    help="The location you want to query the air quality information from.")
parser.add_argument(
    "-t", "--token", help="Your API token for waqi.info.", required=True)
args = parser.parse_args()

if not args.location:
    loc_url = "https://location.services.mozilla.com/v1/geolocate?key=geoclue"
    with urllib.request.urlopen(loc_url) as url:
        data = json.load(url)
        latitude = float(data["location"]["lat"])
        longitude = float(data["location"]["lng"])
        location = "geo:{};{}".format(latitude, longitude)
else:
    location = args.location

api_url = "https://api.waqi.info/feed/{}/?token={}".format(location, args.token)
with urllib.request.urlopen(api_url) as url:
    jsondata = json.load(url)
    data = jsondata["data"]
    aqi = int(data["aqi"])
    output = {
        "text": get_level(aqi),
        "class": get_class(aqi),
        "tooltip": get_tooltip(data)
    }
    print(json.dumps(output))
