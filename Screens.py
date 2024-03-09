import kivy
from kivy.config import Config
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from detector_status_scraper import get_result
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase
import matplotlib.pyplot as plt
from detector_status_scraper import get_graph_data
from detector_status_scraper import graf
from graceDB_scraper import graceDB
from kivy.uix.widget import Widget
from kivy.garden.matplotlib.backend_kivy import FigureCanvasKivy
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
import os
from kivy.uix.popup import Popup
import threading
import time
from kivy.uix.modalview import ModalView
from kivy.core.audio import SoundLoader
import pickle
import time

kivy.require('2.2.1')  # Set the required Kivy version

# Set window borderless
Config.set('graphics', 'borderless', '1')

# Define custom fonts HERE
LabelBase.register(name='TimesNewRoman', fn_regular='./Desktop/new-alarm/fonts/TimesNewRoman/times_new_roman.ttf')
LabelBase.register(name='TimesNewRomanBOLD', fn_regular='./Desktop/new-alarm/fonts/TimesNewRoman/times_new_roman_bold.ttf')
LabelBase.register(name='ArialBOLD', fn_regular='./Desktop/new-alarm/fonts/Arial/ArialBOLD.ttf')

########SCREEN 1
class ScreenOne(Screen):
    def __init__(self, **kwargs):
        super(ScreenOne, self).__init__(**kwargs)

        # Set background color
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Set background color to white
            self.rect = Rectangle(pos=self.pos, size=self.size)


        # Fetch data from grafana website using the custom library
        names, statuses, durations = get_result()

        # Create GridLayout for the table
        layout = GridLayout(cols=3, spacing=1, padding=1, size_hint=(None, None), width=550)  # adjust this width parameter if font needs to be changed for the table

        # Set the height and width for the cells
        cell_height = 40
        cell_width = 200

        # Define the colors as an RGBA tuple
        #cell_color_header = (201/255, 184/255, 166/255, 1) #color #c9b8a6 in RGBA

        # Add table headers
        for header_text in ['Detector', 'Status', 'Duration [h:min]']:
            header_label = Label(text=header_text, font_size='25sp',size_hint_y=None, height=cell_height, width = cell_width, halign='center', valign='middle', color=(0, 0, 0, 1))
            layout.add_widget(header_label)

        with layout.canvas.before:
            Color(201/255, 184/255, 166/255, 1) #color #c9b8a6 in RGBA
            self.header_rect = Rectangle(pos=(layout.x + 50, layout.y + layout.height + 480), size = (layout.width, 40))

        # Populate the GridLayout with data
        for name, status, duration in zip(names, statuses, durations):
            for text in [name, status, f"{duration[0]}:{duration[1]}"]:
                cell_label = Label(text=text, font_size='25sp',size_hint_y=None, height=cell_height, width = cell_width, halign='center', valign='middle', color=(0, 0, 0, 1))
                layout.add_widget(cell_label)

        # Calculate height of the layout based on number of items
        layout.height = len(names) * 40 + 40  # 40 for header row

        # Fixed width of the layout
        layout_width = 700

        # Setting the position of the layout here
        layout.x = (Window.width - layout_width) / 2
        layout.y = (Window.height - layout.height) / 2 + 200

        # Add the GridLayout to the screen
        self.add_widget(layout)

        # Draw grid lines
        with layout.canvas.before:
            Color(0, 0, 0, 1)  # Set color of grid lines to black
            for i in range(1, 3):  # Draw vertical lines
                x = layout.x + layout.width / 3 * i
                Rectangle(pos=(x - 0.03, layout.y), size=(1, layout.height))
            for i in range(1, len(layout.children) // 3):  # Draw horizontal lines
                y = layout.y + layout.height / (len(layout.children) // 3) * i
                Rectangle(pos=(layout.x, y - 0.03), size=(layout.width, 1))

        graph_path = "/home/GWalarm-v3/Desktop/new-alarm/plots/GwistatGraph.png"
        error_path = "/home/GWalarm-v3/Desktop/new-alarm/plots/GwistatError1.png"

        if os.path.exists(graph_path):
            # Image file exists, load it
            self.image = Image(source = graph_path)
        else:
            # Image file does not exist, load alternative image
            self.image = Image(source = error_path, size_hint=(None, None), size=(1000, 1000), pos_hint={'right': 0.90, 'bottom': 0.90})

        self.add_widget(self.image)


        # Load and display an image
        image_path = './Desktop/new-alarm/pictures/IGR_logo.jpg'
        self.image = Image(source=image_path, size_hint=(None, None), size=(200, 200), pos_hint={'right': 0.97, 'top': 1})
        self.add_widget(self.image)

        # Load and display an image
        image_path = './Desktop/new-alarm/pictures/LIGO_detectors.jpg'
        self.image = Image(source=image_path, size_hint=(None, None), size=(630, 500), pos_hint={'left': 0.97, 'bottom': 1})
        self.add_widget(self.image)

        # Load and display an image
        image_path = './Desktop/new-alarm/pictures/Map.jpg'
        self.image = Image(source=image_path, size_hint=(None, None), size=(700, 500), pos_hint={'left': 1, 'top': 1})
        self.add_widget(self.image)

        # Add Label for additional information
        self.reference_label = Label(
            text="Live data obtained from online.igwn.org\nImage reproduced from ligo.caltech.edu",
            font_size='25sp',
            size_hint=(None, None),
            size=(1500, 400),
            pos_hint={'x':0.03, 'y': -0.10},
            color=(0, 0, 0, 1),
            halign='left',
            valign='bottom',
            text_size=(None, None)
        )
        self.reference_label.bind(texture_size=self._update_reference_label_size)
        self.add_widget(self.reference_label)

        # Bind size of Rectangle to size of Screen
        self.bind(size=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size

    def _update_reference_label_size(self, instance, value):
        self.reference_label.text_size = (instance.width, None)

########SCREEN 2
class ScreenTwo(Screen):
    def __init__(self, **kwargs):
        super(ScreenTwo, self).__init__(**kwargs)

        # Set background image
        with self.canvas.before:
            #self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source='./Desktop/new-alarm/pictures/Facts_Background.jpg', pos=self.pos, size=self.size)

        # Bind size of Rectangle to size of Screen
        self.bind(size=self._update_rect)

        # List of strings to alternate between
        # ADD ANY ADDITIONAL GRAVITATIONAL WAVE FACTS HERE:)
        self.texts = [
            "Gravitational waves are 'ripples' in space-time caused by some of the most violent and energetic processes in the Universe.",
            "Albert Einstein predicted the existence of gravitational waves in 1916 in his general theory of relativity.",
            "The cosmic ripples - gravitational waves - travel at the speed of light.",
            "Gravitational waves carry with them information about their origins, as well as clues to the nature of gravity itself.",
            "The strongest gravitational waves are produced by colliding black holes, supernovae, and colliding neutron stars.",
            "The first gravitational wave detection was made by LIGO on September 14, 2015."
        ]
        self.current_text_index = 0

        self.text_label = Label(
            text=self.texts[self.current_text_index],
            font_size='55sp',
            font_name='ArialBOLD',
            size_hint=(None, None),
            size=(1000, 900),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            text_size=(None, None)
        )
        self.text_label.bind(texture_size=self._update_label_size)
        self.add_widget(self.text_label)

        # for additional information
        self.additional_info_label = Label(
            text="Image reproduced from ligo.caltech.edu\nFor more information visit the official IGR website: gla.ac.uk/schools/physics/research/groups/igr/",
            font_size='25sp',
            size_hint=(None, None),
            size=(1500, 400),
            pos_hint={'x':0.03, 'y': -0.10},
            color=(1, 1, 1, 1),
            halign='left',
            valign='bottom',
            text_size=(None, None)
        )
        self.additional_info_label.bind(texture_size=self._update_additional_info_label_size)
        self.add_widget(self.additional_info_label)

        # Schedule updating the facts every 15 seconds (or CHANGE TIME HERE here)
        Clock.schedule_interval(self.update_text, 15)

        # Load and display an image
        image_path = './Desktop/new-alarm/pictures/IGR_logo_negative.png'
        self.image = Image(source=image_path, size_hint=(None, None), size=(300, 300), pos_hint={'right': 0.97, 'bottom': -1})
        self.add_widget(self.image)

    def update_text(self, dt):
        self.current_text_index = (self.current_text_index + 1) % len(self.texts)
        self.text_label.text = self.texts[self.current_text_index]

    def _update_rect(self, instance, value):
        self.bg_rect.size = instance.size

    def _update_label_size(self, instance, value):
        self.text_label.text_size = (instance.width, None)

    def _update_additional_info_label_size(self, instance, value):
        self.additional_info_label.text_size = (instance.width, None)

########SCREEN 3

class ScreenThree(Screen):
    def __init__(self, **kwargs):
        super(ScreenThree, self).__init__(**kwargs)
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_rect, pos=self._update_rect)

        title_label = Label(
        text = 'O4 Latest Gravitational Wave Detections',
        font_size = '60sp',
        font_name='ArialBOLD',
        size_hint=(1,None),
        height = 1950,
        halign='center',
        valign='middle',
        color=(0,0,0,1))
        self.add_widget(title_label)

        title_label = Label(
        text = 'BBH = Binary Black Hole; NSBH = Neutron Star-Black Hole Binary; BNS = Binary Neutron Star',
        font_size = '25sp',
        font_name='ArialBOLD',
        size_hint=(1,None),
        height = 128,
        halign='center',
        valign='middle',
        color=(0,0,0,1))
        self.add_widget(title_label)

        title_label = Label(
        text = 'For more information visit gracedb.ligo.org',
        font_size = '25sp',
        size_hint=(1,None),
        height = 75,
        halign='center',
        valign='middle',
        color=(0,0,0,1))
        self.add_widget(title_label)

        # Fetch data from graceDB
        eventnames, dates, eventorigin, eventFAR = graceDB()

        # Create GridLayout for the table
        layout = GridLayout(cols=4, spacing=1, padding=1, size_hint=(None, None), width=1800)  # adjust this width parameter if font needs to be changed for the table

        # Set the height and width for the cells
        cell_height = 52
        cell_width = 650

        # Add table headers
        for header_text in ['Event Name', 'Date and Time', 'Possible Source (Probability) ', 'False Alarm Rate']:
            header_label = Label(text=header_text, font_size='25sp', size_hint_y=None, height=cell_height, width=cell_width, halign='center', valign='middle', color=(0, 0, 0, 1))
            layout.add_widget(header_label)

        with layout.canvas.before:
            Color(146/255, 180/255, 227/255, 1) #color #92b4e3 in RGBA
            self.header_rect = Rectangle(pos=(layout.x + 50, layout.y + layout.height + 635), size = (layout.width, 50))  #adjust the number after layout.height for height of blue rectangle

        # Populate the GridLayout with data
        for event_name, date, event_origin, event_FAR in zip(eventnames, dates, eventorigin, eventFAR):
            for text in [event_name, date, event_origin, event_FAR]:
                cell_label = Label(text=text, font_size='25sp', size_hint_y=None, height=cell_height, width=cell_width, halign='center', valign='middle', color=(0, 0, 0, 1))
                layout.add_widget(cell_label)

        # Calculate height of the layout based on number of items
        layout.height = len(eventnames) * cell_height + cell_height  # Adjusted for header row

        # Center the GridLayout
        layout.x = (Window.width - layout.width) / 2 + 550   #adjust the last number to move table on x axis
        layout.y = (Window.height - layout.height) / 2 + 200

        # Add the GridLayout to the screen
        self.add_widget(layout)

        # Draw grid lines
        with layout.canvas.before:
            Color(0, 0, 0, 1)  # Set color of grid lines to black
            for i in range(1, 4):  # Draw vertical lines
                x = layout.x + layout.width / 4 * i
                Line(points=[x, layout.y, x, layout.y + layout.height], width=1)
            for i in range(1, len(layout.children) // 4):  # Draw horizontal lines
                y = layout.y + layout.height / (len(layout.children) // 4) * i
                Line(points=[layout.x, y, layout.x + layout.width, y], width=1)

        # Load and display an image
        image_path = './Desktop/new-alarm/pictures/IGR_logo.png'
        self.image = Image(source=image_path, size_hint=(None, None), size=(200, 200), pos_hint={'right': 0.97, 'top': 1})
        self.add_widget(self.image)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size

#########SCREEN 4

class ScreenFour(Screen):
    def __init__(self, **kwargs):
        super(ScreenFour, self).__init__(**kwargs)
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_rect, pos=self._update_rect)

        title_label = Label(
        text = 'Latest Gravitational Wave Detection',
        font_size = '60sp',
        font_name='ArialBOLD',
        size_hint=(1,None),
        height = 1950,
        halign='center',
        valign='middle',
        color=(0,0,0,1))
        self.add_widget(title_label)

        eventnames, dates, event_origin, event_FAR = graceDB()
        eventname, date, last_event_origin, last_event_FAR = eventnames[0], dates[0], event_origin[0], event_FAR[0]

        # Display the information
        title_label = Label(text=f"[font=ArialBOLD]Event Name:[/font] {eventname}\n"f"[font=ArialBOLD]Date:[/font] {date}\n"f"[font=ArialBOLD]Source:[/font] {last_event_origin}\n"f"[font=ArialBOLD]False Alarm Rate:[/font] {last_event_FAR}\n",
        markup = True,
        font_size = '40sp',
        size_hint=(1,None),
        height = 480,
        size=(1500, 400),
        pos_hint={'x':-0.2, 'y': 0.35},
        halign='left',
        valign='middle',
        color=(0,0,0,1))
        self.add_widget(title_label)

        # Load and display an image
        image_path = './Desktop/new-alarm/pictures/IGR_logo.png'
        self.image = Image(source=image_path, size_hint=(None, None), size=(300, 300), pos_hint={'right': 0.97, 'bottom': -1})
        self.add_widget(self.image)

        # Load and display an image
        image_path = '/home/GWalarm-v3/Desktop/new-alarm/maps/first_map.png'
        self.image = Image(source=image_path, size_hint=(None, None), size=(1000, 1000), pos_hint={'right': 0.98, 'top': 0.97})
        self.add_widget(self.image)

        self.reference_label = Label(
            text="Live data obtained from gracedb.ligo.org",
            font_size='25sp',
            size_hint=(None, None),
            size=(1500, 400),
            pos_hint={'x':-0.25, 'y': -0.10},
            color=(0, 0, 0, 1),
            halign='left',
            valign='bottom',
            text_size=(None, None)
        )
        self.add_widget(self.reference_label)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size

#MAKING THE SCREEN ALTERNATE

class WindowManager(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        self.manager = WindowManager()
        self.screen_one = ScreenOne(name='screen_one')
        self.screen2 = ScreenTwo(name='screen_two')
        self.screen3 = ScreenThree(name='screen_three')
        self.screen4 = ScreenFour(name='screen_four')
        self.manager.add_widget(self.screen_one)
        self.manager.add_widget(self.screen2)
        self.manager.add_widget(self.screen3)
        self.manager.add_widget(self.screen4)

        # For checking new events
        self.eventnames_once = self.load_eventnames_once()
        # Schedule the event checking function to run every 10 seconds
        self.event_check_timer = Clock.schedule_interval(self.check_for_new_events, 10)

        self.switch_screen_timer = Clock.schedule_interval(self.switch_screen, 45) #CHNAGE TIME HERE FOR CYCLING OF SCREENS (IN SECONDS)
        self.set_window_maximized()
        return self.manager



    def set_window_maximized(self):
        Window.size = (1, 1)  # Set initial size to ensure maximize works on some systems
        Window.borderless = True
        Window.fullscreen = 'auto'

    def switch_screen(self, dt):
        current_screen_name = self.manager.current
        if current_screen_name == 'screen_one':
            self.manager.current = 'screen_two'
        elif current_screen_name == 'screen_two':
            self.manager.current = 'screen_three'
        elif current_screen_name == 'screen_three':
            self.manager.current = 'screen_four'
        else:
            self.manager.current = 'screen_one'


    def load_eventnames_once(self):
        if os.path.exists("eventnames_once.pkl"):
            with open("eventnames_once.pkl", "rb") as f:
                return pickle.load(f)
        else:
            return []

    def save_eventnames_once(self):
        with open("eventnames_once.pkl", "wb") as f:
            pickle.dump(self.eventnames_once, f)

    def check_for_new_events(self, dt):
        eventnames = graceDB()  # Call graceDB function to get the latest events

        new_events = [event for event in eventnames if event not in self.eventnames_once]

        if new_events:
            self.show_popup(new_events)
            self.eventnames_once = eventnames
            self.save_eventnames_once()


    # Customizing the pop up message
    def show_popup(self, new_events):

        #event_info_lines = []
        #for event in new_events:
           # if isinstance(event, list):
            #    # If event is a list, join its elements and treat it as a single string
            #    event_str = ", ".join(event)
            #    event_info_lines.append(f"{event_str}")
           # else:
                # If event is not a list, split the string to extract key-value pairs
              #  event_info = event.split(":")
             #   if len(event_info) == 4:
            #        # Extracting values for Name, Origin, Date, and FAR
           #         name = event_info[0].strip()
          #          origin = event_info[1].strip()
         #           date = event_info[2].strip()
         #           far = event_info[3].strip()
                    # Constructing the line with required format
         #           event_info_lines.append(f"Name: {name}\nOrigin: {origin}\nDate: {date}\nFAR: {far}")

        # Join the formatted information lines
        #new_events_text = "\n".join(event_info_lines)
        #content = Label(text=f"ATTENTION! New event(s) detected:\n{new_events_text}", color=(1, 0, 0, 1), font_size=45)
        #content = Label(text=f"ATTENTION! New gravitational wave event was detected:\n{new_events_text}", color = (1,0,0,1), font_size = 45)
        content = Label(text="ATTENTION! A new gravitational wave event has been detected!\n", color = (1,0,0,1), font_size = 45)

        popup = Popup(title="Gravitational Wave Alert",
        content=content,
        size_hint=(None, None),
        size=(1400, 800),
        title_size = 35,
        title_color = (1, 1, 1, 1),
        separator_color = (1, 1, 1, 1),
        background_color = (0, 0, 0, 1),
        auto_dismiss = True
        )

        sound = SoundLoader.load('/home/GWalarm-v3/Desktop/new-alarm/sounds/chirp.mp3')

        # Play the sound when the popup opens
        if sound:
            sound.play()

        popup.open()

        # Dismiss the popup after 60 seconds, CHANGE TIME HERE IF NEEDED
        Clock.schedule_once(popup.dismiss, 60)

#The following is to run the app, i.e. RUN the screens
if __name__ == '__main__':
    MyApp().run()