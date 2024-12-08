import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import requests
import google.generativeai as genai
# import openai
# from openai import OpenAI
import pygame
from openai import OpenAI
from bs4 import BeautifulSoup
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import Gesture_Controller
#import Gesture_Controller_Gloved as Gesture_Controller
import app
from threading import Thread
from os.path import isdir, join

# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ----------------Variables------------------------
file_exp_status = False
files =[]
path = ''
is_awake = True  #Bot status

# Initialize pygame mixer
pygame.mixer.init()



# ----------------openai------------------------
# openai.api_key = "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"
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)
genai.configure(api_key="AIzaSyDs0JXWvUyIR8l0TY2RC_8YrTH9uYsUwgQ")
# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(audio)
    engine.say(audio)
    engine.runAndWait()


def wish():
    hour = int(datetime.datetime.now().hour)

    if hour>=0 and hour<12:
        reply("Good Morning!")
    elif hour>=12 and hour<18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")  
        
    reply("I am NAB'S, how may I help you?")

# Set Microphone parameters
with sr.Microphone() as source:
        r.energy_threshold = 500
        r.dynamic_energy_threshold = False

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Plz check your Internet connection')
        except sr.UnknownValueError:
            print('cant recognize')
            pass
        return voice_data.lower()

# Greater length wait Audio tp string
def greater_record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 1.8
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Plz check your Internet connection')
        except sr.UnknownValueError:
            print('cant recognize')
            pass
        return voice_data.lower()


# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print(voice_data)
    voice_data.replace('Nabs',' ')
    app.eel.addUserMsg(voice_data)

    if is_awake==False:
        if 'wake up' in voice_data:
            is_awake = True
            wish()

    # STATIC CONTROLS
    elif 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is Nabs!')

    elif 'date' in voice_data:
        reply(today.strftime("%B %d, %Y"))

    elif 'time' in voice_data:
        reply(str(datetime.datetime.now()/2).split(" ")[1].split('.')[0])

    elif "refresh" in voice_data or "refesh" in voice_data:
        refresh_desktop()

    elif 'search' in voice_data:
        reply('Searching for ' + voice_data.split('search')[1])
        url = 'https://google.com/search?q=' + voice_data.split('search')[1]
        try:
            webbrowser.get().open(url)
            reply('This is what I found!')
        except:
            reply('Please check your browser Internet')

    elif 'location' in voice_data:
        reply('Which place are you looking for ?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/&amp;'
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')

    elif 'youtube' in voice_data:
        url = 'https://youtube.com'
        try:
            webbrowser.get().open(url)
            reply('opening youtube. what do you want to play')
            temp_audio = record_audio()
            reply('playing...')
            # url = 'https://www.youtube.com/results?search_query='+temp_audio
            url=search_youtube(temp_audio,video_choice=1)
            webbrowser.get().open(url)
            reply('Here is the results')
        except:
            reply('Please check your Internet')


    elif ('bye' in voice_data) or ('by' in voice_data) or ('buy' in voice_data) or ('bhai' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        is_awake = False

    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        #sys.exit() always raises SystemExit, Handle it in main loop
        sys.exit()

    elif 'list desktop' in voice_data or 'desktop' in voice_data:  # Generalizing the misspelling check
        desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")  # Using dynamic user folder
        try:
            # List all items on the Desktop
            items = os.listdir(desktop_path)
            if items:
                files = []
                folders = []
                for item in items:
                    item_path = os.path.join(desktop_path, item)
                    if os.path.isdir(item_path):
                        folders.append(item)
                    else:
                        # Get the file name without the extension
                        file_name, _ = os.path.splitext(item)
                        files.append(file_name)

                # Format the output
                output_str = ""
                c = 0
                # Adding folder items
                for f in folders:
                    c += 1
                    print(f"{c} : {f}")
                    output_str += f"{c}: {f}<br>"

                # Adding file items
                for fi in files:
                    c += 1
                    print(f"{c} : {fi}")
                    output_str += f"{c}: {fi}<br>"
                reply("Here are the list of desktop files and folders:")
                app.ChatBot.addAppMsg(output_str)
            else:
                reply('No files or folders found on your Desktop.')
        except Exception as e:
            reply(f'An error occurred while accessing the Desktop: {e}')


   # DYNAMIC CONTROLS
    elif 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target = gc.start)
            t.start()
            reply('Launched Successfully')

    elif ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped')
        else:
            reply('Gesture recognition is already inactive')

    elif 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied')

    elif 'page' in voice_data or 'pest'  in voice_data or 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted')

    # File Navigation (Default Folder set to C://)
    elif 'list' in voice_data:
        counter = 0
        path = 'C://'
        files = listdir(path)
        filestr = ""
        for f in files:
            counter+=1
            print(str(counter) + ':  ' + f)
            filestr += str(counter) + ':  ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)

    elif file_exp_status == True:
        counter = 0
        if 'open' in voice_data:
            if isfile(join(path,files[int(voice_data.split(' ')[-1])-1])):
                os.startfile(path + files[int(voice_data.split(' ')[-1])-1])
                file_exp_status = False
            else:
                try:
                    path = path + files[int(voice_data.split(' ')[-1])-1] + '//'
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter+=1
                        filestr += str(counter) + ':  ' + f + '<br>'
                        print(str(counter) + ':  ' + f)
                    reply('Opened Successfully')
                    app.ChatBot.addAppMsg(filestr)
                except:
                    reply('You do not have permission to access this folder')
        if 'back' in voice_data:
            filestr = ""
            if path == 'C://':
                reply('Sorry, this is the root directory')
            else:
                a = path.split('//')[:-2]
                path = '//'.join(a)
                path += '//'
                files = listdir(path)
                for f in files:
                    counter+=1
                    filestr += str(counter) + ':  ' + f + '<br>'
                    print(str(counter) + ':  ' + f)
                reply('ok')
                app.ChatBot.addAppMsg(filestr)

    elif 'thanks' in voice_data or 'thank you so much' in voice_data or 'thank' in voice_data:
        reply("You're welcome!  If you have any more questions or need further assistance, feel free to ask.")

    #playing music
    elif 'play music' in voice_data or 'play songs' in voice_data or 'play song' in voice_data:
        music_dir = 'C:\\Users\\satis\\Music'
        songs = os.listdir(music_dir)
        mp3_files = [file for file in songs if file.endswith('.mp3')]
        cur_idx=0
        # song_path = os.path.join(music_dir, mp3_files[cur_idx])
        while True:
            current_song = mp3_files[cur_idx]
            song_path = os.path.join(music_dir, current_song)
            reply("playing..")
            play_song(song_path)

            #wait for stop, change song cmds
            temp_audio = greater_record_audio()
            if "stop" in temp_audio:
                pygame.mixer.music.stop()
                reply("music player stopped.")
                break

            elif 'next song' in temp_audio:
                pygame.mixer.music.stop()  # Stop current song
                cur_idx = (cur_idx + 1) % len(mp3_files)  # Go to next song
                reply("Playing next song...")

            elif 'previous song' in temp_audio or 'back' in temp_audio:
                pygame.mixer.music.stop()  # Stop current song
                cur_idx = (cur_idx - 1) % len(mp3_files)  # Go to previous song
                reply("Playing previous song...")
            else:
                pygame.time.delay(9000)
                pygame.mixer.music.stop()

    else:
        # uncommnet the below code. if you don't want LLM's(GPT's) responces
        # reply('I am not functioned to do this !')
        # temp_audio = record_audio()
        # if 'why' in temp_audio:
        #     reply("Because i'm still in the development phase!")
        answer = get_answer_from_chatgpt(voice_data)
        reply(answer)
        print(f"Requests used today: {get_usage()}")
        time.sleep(1)

 # 1) searching on youtube
from selenium import webdriver

def search_youtube(query, video_choice=1):
    query = str(query)  # Ensure the query is a string
    print(f"Search query: {query}")
    
    search_url = f'https://www.youtube.com/results?search_query={query}'
    driver = webdriver.Chrome()  # You can use any driver (e.g., Firefox)
    driver.get(search_url)
    time.sleep(1)  # Wait for 2 seconds to ensure content is fully loaded
    soup = BeautifulSoup(driver.page_source, 'html.parser') # Get page source after JavaScript has loaded the content
    video_links = []
    for link in soup.find_all('a', href=True):
        if '/watch?' in link['href']:
            video_links.append(f"https://www.youtube.com{link['href']}")
    driver.quit()  # Close the browser after extraction
    if video_links:
        return video_links[video_choice - 1]
    else:
        print("No video links found.")
        return None
    # try:
    #     response = requests.get(search_url)
    #     if response.status_code == 200:
    #         soup = BeautifulSoup(response.text, 'html.parser')
    #         # print(soup)
    #         # Get all video links (YouTube video URLs are embedded in 'href' attributes)
    #         video_links = []
    #         for link in soup.find_all('a', href=True):
    #             if '/watch?' in link['href']:
    #                 video_links.append(f"https://www.youtube.com{link['href']}")
    #         for v in video_links:
    #             print(video_links)
    #         # Check if there are video links found
    #         if video_links:
    #             # Return the video URL based on user choice (1st or 2nd result)
    #             return video_links[video_choice - 1]
    #         else:
    #             print("No video links found.")
    #             return None
    #     else:
    #         print("Failed to retrieve YouTube search results. Status code: "+str(response.status_code))
    #         return None
    # except Exception as e:
    #     print(f"Error while searching YouTube:"+e)
    #     return None

# 2) refreshing youtube
def refresh_desktop():
    pyautogui.rightClick()
    time.sleep(1)
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('enter')  # Select "Refresh"
    reply("Desktop refreshed using right-click menu.")

# 3) Function to get an answer from ChatGPT
request_count = 0
MAX_REQUESTS_PER_DAY = 10
def get_usage():
    return request_count
def get_answer_from_chatgpt(question):
    global request_count
     # Check if the daily request limit has been reached
    if request_count >= MAX_REQUESTS_PER_DAY:
        return "Sorry, you've reached your daily request limit."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                # {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user", 
                    "content": question
                }
            ]
        )
        print(response.choices[0].message.content)
        answer = response.choices[0].message.content
        request_count += 1
        return answer
    except Exception as e:
        print(f"Error while fetching answer: {e}")
        return "Sorry, I couldn't find an answer to that question."

# 4) Function to get an answer from ChatGPT

# def get_answer_from_gemini(question):
#     try:
#         model = genai.GenerativeModel("gemini-pro")
#         # Generate text
#         prompt = question
#         response = model.generate_text(prompt=prompt)
#         print(response.text)
#         reply(response.text)
#     except Exception as e:
#         print(f"Error while fetching answer: {e}")
#         return "Sorry, I couldn't find an answer to that question."

# 5) Function to play a specific song from the playlist
def play_song(song_path):
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()  # Play the song
# ------------------Driver Code--------------------

t1 = Thread(target = app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        #take input from GUI
        voice_data = app.ChatBot.popUserInput()
    else:
        #take input from Voice
        voice_data = record_audio()

    #process voice_data
    if voice_data:
        try:
            #Handle sys.exit()
            respond(voice_data)
        except SystemExit:
            reply("Exit Successfull")
            break
        except:
            #some other exception got raised
            print("EXCEPTION raised while closing.")
            break
