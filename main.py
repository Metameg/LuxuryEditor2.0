import os
import streamlit as st
from func.req import *
from func.create_collage import create_video_collage
import json

FPS = 30

overlay_folder = None
is_overlay = False
username = None
download_more_videos = True
is_tiktok_content = False
video_folder = None
song_folder = None
videos = []
clone_tiktok = True
export_folder = 'output'

st.title("Luxury AI")

overlays_folder = "overlays"

create_directories()
install_requirements()

# Sidebar for user input
st.sidebar.header("Settings")

if st.sidebar.checkbox("Import media from local storage"):
    clone_tiktok = False
    video_folder = st.sidebar.text_input("Video Folder Path")
    song_folder = st.sidebar.text_input("Song Folder Path")

if clone_tiktok:
    if st.sidebar.checkbox("Clone content from Tiktok", value=clone_tiktok):
        username = st.sidebar.text_input("Enter TikTok username (e.g., @oclipia):")
        count = st.sidebar.number_input(f"How many videos you want to get from {username}? (ensure that the number of clips you are getting is available on {username} page)", min_value=5, max_value=100, value=10, step=1)

        if username and count:
            st.write(username, count)
            # Scrape TikTok data
            tiktok_data = scrape(user=username, count=count, cursor=0)

            if tiktok_data:
                with st.status(f"{username} Videos"):
                    for tiktok in tiktok_data:
                        st.video(tiktok)

                video_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), username)


                st.write(f"Video Folder {video_folder}")


                if st.sidebar.checkbox("Import song from path"):
                    song_folder = st.sidebar.text_input("Song Folder Path")
                elif st.sidebar.checkbox("Import a viral song"):
                    song_folder = video_folder

                is_tiktok_content = True

if st.sidebar.checkbox("Include watermark"):
    is_overlay = True
    overlay_folder = st.sidebar.text_input("Watermark Folder Path")

if video_folder:
    number_of_videos = 20
    video_files = []

    if os.path.exists(video_folder):
        # Get all video file names in the specified folder
        video_files = [file for file in os.listdir(video_folder) if file.endswith((".mp4", ".mov"))]
        st.toast(f"Found {len(video_files)} videos in `{video_folder}` in your storage", icon="✅")

        number_of_videos = len(video_files)

    if is_tiktok_content:
        number_of_videos = count
        if len(video_files) > 30:
            download_more_videos = False
            st.sidebar.info(f"Found {len(video_files)} videos for {username} in your storage")
            if st.sidebar.checkbox("Download more videos"):
                download_more_videos = True

    num_videos = st.sidebar.slider("Number of Videos to Use", 1, number_of_videos, min(20, number_of_videos))
    duration_length = st.sidebar.slider("Result Clips Duration (seconds)", 1, 90, 10)
    videos_count = st.sidebar.slider("Number of Luxury Clips to Create", 1, 10, 1)

exported_videos_paths = []
with open("sys.json", "r") as file:
    data = json.load(file)

for exported_video_path in data['export']['exported_videos']:
    exported_videos_paths.append(exported_video_path)

if exported_videos_paths:
    st.subheader("Edited Videos")
    with st.status("Loading videos..."):
        for i, exported_video_path in enumerate(exported_videos_paths):
            video_counter = video_count(i)
            try:
                st.video(exported_video_path)
           
                if st.button(f'Remove {video_counter}', key=i):
                    try:
                        os.remove(exported_video_path)
                        remove_video_path(exported_video_path)
                    except OSError as e:
                        st.error(f"Couldn't remove video due to {str(e)}")
            except:
                st.error(f"Couldn't find {exported_video_path}")
                remove_video_path(exported_video_path)

if video_folder and num_videos and song_folder:
    if is_overlay and overlay_folder is None:
        st.error("Make sure to specify an overlay path")
    else:
        if st.sidebar.button("Create Luxury"):
            if is_tiktok_content:
                if download_more_videos:
                    # Download videos
                    download(tiktok_data, username)
            create_video_collage(video_folder, num_videos, song_folder, overlay_folder, export_folder, videos_count, duration_length, is_tiktok_content)