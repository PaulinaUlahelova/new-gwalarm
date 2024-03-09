from bs4 import BeautifulSoup
import requests
import re
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import os
import pickle
import time
#from playsound import playsound

# Global variable to store previously collected event names
previous_eventnames = set()

# Function for scraping info off the gracedb website
def graceDB():
    base_url = "https://gracedb.ligo.org"
    url = f"{base_url}/superevents/public/O4/"
    r = requests.get(url)

    text_with_tr_prepended = r.text.replace("""<td style="min-width: 100px;">
            <a href="/superevents/""", """<tr><td style="min-width: 100px;">
            <a href="/superevents/""")

    # text_with_tr_prepended = re.sub("<br>(.*)<\/br>", "<br/>", text_with_tr_prepended)
    # text_with_tr_prepended = r.text.replace("</br>", "")
    # print(text_with_tr_prepended)
    soup = BeautifulSoup(text_with_tr_prepended, "html.parser")

    eventnames = []
    eventFAR = []
    dates = []
    eventorigin = []
    eventimages = []

    # Track the number of event names collected
    count = 0

    for row in soup.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) >= 2:
            event_name = columns[0].text.strip()
            event_origin = columns[1].text.strip()
            date = columns[3].contents[2].strip()

            if len(columns[3]) > 4:
                date += " " + str(columns[3].contents[4]).strip()

            elif len(columns[3]) == 4:
                extr = re.sub("<\/br>|<br>|\\n", "", str(columns[3].contents[3]))
                date += " " + extr.strip()

            eventimages.append(base_url + columns[5].contents[1].contents[1]["src"])

            event_FAR = columns[6].contents[4].text.strip()
            eventnames.append(event_name)
            dates.append(date)
            eventorigin.append(event_origin)
            eventFAR.append(event_FAR)
            count += 1

            # Play sound when a new event is detected
#            if count == 1:
#                playsound('./Desktop/new-alarm/sounds/chirp.mp3')

            # Break the loop if 10 events are collected
            if count == 10:
                break
            event_imgs = []

            # Download and display the images (ALL OF THEM)
            #for i, event_image_url in enumerate(eventimages):
            #    response = requests.get(event_image_url)
            #    event_img = Image.open(BytesIO(response.content))
            #    event_imgs.append(event_img)
            #    event_img.show()


    save_directory = "/home/GWalarm-v3/Desktop/new-alarm/maps"

    # Ensure that the directory exists, if not create it
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Download only the first image
    if eventimages:
        first_image_url = eventimages[0]
        response = requests.get(first_image_url)
        event_img = Image.open(BytesIO(response.content))
        # Display the image
        #event_img.show()

        # Download and save the first image
        image_filename = "first_map.png"
        image_path = os.path.join(save_directory, image_filename)
        event_img.save(image_path)

    #print("Number of rows with enough data:", count)
    #print("Event Names:", eventnames)
    #print("Event Dates:", dates)
    #print("Event Origin:", eventorigin)
    #print("False Alarm Rate:", eventFAR)
    #print("Event image urls:", eventimages)

    return eventnames, dates, eventorigin, eventFAR

# Call the function and save the returned values
eventnames, dates, eventorigin, eventFAR = graceDB()

# Now I can use these variables outside the function
print("Event Names:", eventnames)
print("Event Dates:", dates)
print("Event Origin:", eventorigin)
print("False Alarm Rate:", eventFAR)

print("Event Name:", eventnames[0])
print("Date:", dates[0])
print("Origin:", eventorigin[0])
print("False Alarm Rate:", eventFAR[0])

# This is to check for new events
# Call the function to get the latest events
#eventnames = graceDB()

# Save the eventnames array to a file
#if os.path.exists("eventnames_once4.pkl"):
#    with open("eventnames_once.pkl4", "rb") as f:
#        eventnames_once = pickle.load(f)
#else:
#    eventnames_once = []
#    with open("eventnames_once.pkl4", "wb") as f:
#        pickle.dump(eventnames_once, f)

# Compare the arrays to detect new events
#new_events = [event for event in eventnames if event not in eventnames_once]

# If there are new events, print a message and write to a file
#if new_events:
#    print("ATTENTION! New event detected:")
#    for event in new_events:
#        print(event)
    # Write a signal to a file to notify the Kivy application
#    with open("signal.txt", "w") as f:
#        f.write("new_event")

# Update eventnames_once with the current eventnames array
#eventnames_once = eventnames

# Save the updated eventnames_once array to a file
#with open("eventnames_once.pkl4", "wb") as f:
#    pickle.dump(eventnames_once, f)