import time
import requests
import matplotlib.pyplot as plt
from datetime import datetime

# This code is to scrape the information off the gwistat website
API_URL = "https://online.igwn.org/grafana/api"

TIMESTAMP_15_MINUTES = 900_000
TIMESTAMP_NOW = int(time.time() * 1000)

TIMESTAMP_1_HOUR_AGO = TIMESTAMP_NOW - 4 * TIMESTAMP_15_MINUTES

TIMESTAMP_1_MONTH_AGO = TIMESTAMP_NOW - TIMESTAMP_15_MINUTES * 4 * 24 * 31

mapping = {
    "GEO": "GEO600",
    "H1" : "LIGO Hanford",
    "K1" : "KAGRA",
    "L1" : "LIGO Livingston",
    "V1" : "Virgo",
}

def get_status_frames(data):
    return data["results"]["A"]["frames"]

def get_status_from_frame(frame):
    return frame["data"]["values"][1][0]

def get_status_last_update_from_frame(frame):
    return frame["data"]["values"][0][0]

def get_key_from_frame(frame):
    return frame["schema"]["fields"][1]["labels"]["ifo"]

def get_name_from_frame(frame):
    return mapping[get_key_from_frame(frame)]


def get_duration_frames(data):
    return data["results"]["B"]["frames"]

def get_duration_from_frame(frame):
    return frame["data"]["values"][1][0]

def get_data(path):
    """Returns empty list on failure"""
    try:
        json_data = {
            'intervalMs': 7200000,
            'maxDataPoints': 429,
            'timeRange': {
                'from': str(TIMESTAMP_1_MONTH_AGO),
                'to': str(TIMESTAMP_NOW),
            },
        }

        request = requests.request("POST", f"{API_URL}{path}", json=json_data)
        request.raise_for_status()
        return request.json()

    except requests.HTTPError:
        print("failed to fetch data..")
        return []

def get_result():

    result = get_data("/public/dashboards/1a0efabe65384a7287abfcc1996e4c4d/panels/4/query")

    status_frames:list = get_status_frames(result)

    duration_frames = get_duration_frames(result)

    names = []
    statuses = []
    durations = []
    for key, name in mapping.items():
        status_frame = [frame for frame in status_frames if get_key_from_frame(frame) == key]
        if not status_frame:
            status = None
        else:
            last_update = get_status_last_update_from_frame(status_frame[0])
            if TIMESTAMP_1_HOUR_AGO > last_update:
                status = "Data too old"
            else:
                status = get_status_from_frame(status_frame[0])

        statuses.append(status)

        name = mapping[key]
        names.append(name)

        duration_frame = [frame for frame in duration_frames if get_key_from_frame(frame) == key]


        if not duration_frame:
            durations.append("N/A")
            print(name, status, f" duration: N/A")

        else:
            duration_seconds = get_status_from_frame(duration_frame[0])
            m, s = divmod(duration_seconds, 60)
            h, m = divmod(m, 60)

            durations.append([h,m])
            print(name, status, f" duration in seconds: {duration_seconds}", f"duration in 'HH:mm': {h}:{m}")

    statuses = ['No Data' if status is None else status for status in statuses]

    return names, statuses, durations

# Scraping data from the graph on gwistat
def get_graph_frames(data):
    return data["results"]["A"]["frames"]

def get_graph_x_data(frame):
    return frame["data"]["values"][0]

def get_graph_y_data(frame):
    return frame["data"]["values"][1]

def get_graph_data():

    result = get_data("/public/dashboards/1a0efabe65384a7287abfcc1996e4c4d/panels/2/query")

    status_frames:list = get_graph_frames(result)

    data = {}

    for frame in status_frames:
        key = get_key_from_frame(frame)

        x_data = get_graph_x_data(frame)
        x_data = [datetime.fromtimestamp(dp // 1000) for dp in x_data]
        y_data = get_graph_y_data(frame)

        data[key] = [x_data, y_data]

    return data

print(get_result())

print(get_graph_data())



try:
    graf = get_graph_data()

    if graf:
        # PLOTTING THE GRAPHS
        plt.figure(figsize=(10,10))
        # Plot for LIGO Hanford
        plt.plot(graf["H1"][0],graf["H1"][1], label = 'LIGO Hanford')
        # Plot for KAGRA
        plt.plot(graf["K1"][0],graf["K1"][1], label = 'KAGRA')
        # Plot for Virgo
        plt.plot(graf["V1"][0],graf["V1"][1], label = 'Virgo')
        # Plot for GEO600
        plt.plot(graf["GEO"][0],graf["GEO"][1], label = 'GEO600')
        # Plot for LIGO Livingston
        plt.plot(graf["L1"][0],graf["L1"][1], label = 'LIGO Livingston')

        plt.xlabel('Date [Day:Month:Hour]', fontsize = 17)
        plt.ylabel('Distance [Mpc]', fontsize = 17)
        plt.title('History of the Detection Range', fontsize = 17)
        plt.legend(fontsize = 17)
        save_path0 = "/home/GWalarm-v3/Desktop/new-alarm/plots/GwistatGraph.png"
        plt.savefig(save_path0)
        #plt.show()
        # To avoid the plot from being displayed externally
        plt.close()

    else:
        # If any data is missing create empty plot
        plt.figure(figsize=(10,10))
        plt.text(0.5,0.6, 'No Data Available From IGWN at the Moment', horizontalalignment = 'center', verticalalignment = 'center', fontsize = 17, color = 'black')
        plt.text(0.5,0.4, 'Please Check Later', horizontalalignment = 'center', verticalalignment = 'center', fontsize = 17, color = 'red')
        plt.xlabel('Date [Day:Month:Hour]', fontsize = 17)
        plt.ylabel('Distance [Mpc]', fontsize = 17)
        plt.title('History of the Detection Range', fontsize = 17)
        # Save the plot so it can be propagated with kivy
        save_path1 = "/home/GWalarm-v3/Desktop/new-alarm/plots/GwistatError1.png"
        plt.savefig(save_path1)
        #plt.show()
        plt.close()

except KeyError as e:
        # If any data is missing create empty plot
        plt.figure(figsize=(10,10))
        plt.text(0.5,0.6, 'No Data Available From IGWN at the Moment', horizontalalignment = 'center', verticalalignment = 'center', fontsize = 17, color = 'black')
        plt.text(0.5,0.4, 'Please Check Later', horizontalalignment = 'center', verticalalignment = 'center', fontsize = 17, color = 'red')
        plt.xlabel('Date [Day:Month:Hour]', fontsize = 17)
        plt.ylabel('Distance [Mpc]', fontsize = 17)
        plt.title('History of the Detection Range', fontsize = 17)
        # Save the plot so it can be propagated with kivy
        save_path2 = "/home/GWalarm-v3/Desktop/new-alarm/plots/GwistatError2.png"
        plt.savefig(save_path2)
        #plt.show()
        plt.close()