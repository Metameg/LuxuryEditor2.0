import requests
import os
import requests
import streamlit as st
import json
import subprocess
import random
import string

def video_count(i):
    video_counter = "st" if i+1 == 1 else "nd" if i+1 == 2 else "rd" if i+1 == 3 else "th"
    video_counter = str(i+1) + video_counter + " Video"

    return video_counter

def open_json():
    try:
        with open("sys.json", "r") as file:
            data = json.load(file)
            return data
    except json.decoder.JSONDecodeError as e:
        save_json([])
        open_json()

def save_json(data):
    with open("sys.json", "w") as file:
        json.dump(data, file, indent=2)

def remove_video_path(video_path):
    data = open_json()

    data['export']['exported_videos'].remove(video_path)

    save_json(data)

    st.toast("Video removed successfully, refresh!")

def install_requirements():
    data = open_json()

    if not data["requirements"]["installed"]:
        for requirement in data["requirements"]["name"]:
            st.toast(f"Installing {requirement}...")
            subprocess.run(['pip', 'install', requirement])

        data["requirements"]["installed"] = True
    
    save_json(data)

def create_directories():
    os.makedirs("overlays", exist_ok=True)

    if not os.path.exists("sys.json"):
        data = {
            "requirements": {
                'name': ["Pillow==9.4.0", "moviepy==1.0.3"],
                'installed': False,
            },
            "export": {
                "path": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "exported_videos": []
            }
        }
        save_json(data)

def remove_watermark():
    hide_streamlit_style = """
            <style>
            #MainMenu {display: none;}
            footer {display: none;}
            .stDeployButton {display: none;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

def generate_random_string(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def download(res:list, path:str='clips'):
    
    # Create a folder if it doesn't exist
    os.makedirs(path, exist_ok=True)

    with st.status("Downloading clips..."):
        videos_paths = []
        for video_url in res:
            # Send an HTTP GET request to the video URL
            response = requests.get(video_url)

            if response.status_code == 200:
                random_filename = path + "/" + generate_random_string() + ".mp4"
                with open(random_filename, "wb") as file:
                    file.write(response.content)
                videos_paths.append(random_filename)
                st.write(f"Saved {random_filename}")
                st.toast(f"Saved {random_filename}")
            else:
                print("Failed to download the video. Status code:", response.status_code)

        st.success("Downloaded successfully!")

def scrape(user: str, user_id: int = 0, count: int = 15, cursor: int = 0) -> list:
    url = "https://tiktok-video-no-watermark2.p.rapidapi.com/user/posts"
    video_list = []

    # cursor is where starging from. 0 is most recent
    querystring = {
            "unique_id": user,
            "user_id": user_id,
            "count": count,
            "cursor": cursor
            }
    headers = {
            # "X-RapidAPI-Key": st.secrets["x-rapid"],
            "X-RapidAPI-Key": "2327414bf8msh46b87d8f8913dcep10a5a4jsn7b4d54ab5c84",
            "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        response_data = None
        try:
            response_data = response.json()
        except Exception as error:
            print("api data was not in json format as expected")
            print(error)
            return []
        try:
            if response_data.get('msg') != "success":
                print('un-successful api call')
                print(response_data)
                return []
            else:
                data = response_data.get('data')
                if data:
                    videos = data.get('videos')
                    if videos:
                        try:
                            # bug where sometimes more
                            videos = videos[:count]
                            for video in videos:
                                vid_url = video.get('play')
                                if not vid_url:
                                    continue
                                video_list.append(vid_url)
                        except Exception as error:
                            print("error trying to scrape videos from api links")
                            print(error)
                            return []
                    else:
                        print('api json attribute videos not found')
                        return []

                else:
                    print('api json attribute data not found')
                    return []
        except Exception as error:
            print('error accesing json attribute of response')
            print(error)
            return []
        
    return video_list