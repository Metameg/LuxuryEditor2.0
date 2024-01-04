import streamlit as st
import os
from moviepy.editor import VideoFileClip, AudioFileClip
import random

def randomize_files(video_folder, num_videos, song_folder, overlay_folder, duration_length, is_tiktok_content):
    # Get all video file names in the specified folder
    video_files = [file for file in os.listdir(video_folder) if file.endswith((".mp4", ".mov"))]

    if num_videos > len(video_files):
        st.error("The requested number of videos is greater than the number of available videos.")
        return None, None, None

    if not video_files:
        st.error("The folder doesn't contain any videos")
        video_paths = None
    else:
        random.shuffle(video_files)
        selected_video_files = video_files[:num_videos]

        selected_videos_duration = 0

        st.toast("Calculating selected videos duration to match Desired duration...", icon="🧮")
        st.write("Calculating selected videos duration to match Desired duration...")

        for video in selected_video_files:
            try:
                selected_videos_duration += VideoFileClip(os.path.join(video_folder, video)).duration
            except Exception as e:
                st.error(f"Error adding video duration due to {str(e)}, video causing the error: {video}")
                selected_video_files.remove(video)

        while selected_videos_duration < duration_length:
            st.toast(f"Adding new videos to the mix... Reached duration: {selected_videos_duration}s, Desired duration: {duration_length}", icon="🏃")
            st.write(f"Adding new videos to the mix... Reached duration: {selected_videos_duration}s, Desired duration: {duration_length}")
            num_videos += 1
            selected_videos_duration += VideoFileClip(os.path.join(video_folder, random.choice(selected_video_files))).duration
            selected_video_files = video_files[:num_videos]

        st.write(f"Verified! Desired duration: {duration_length}s, Summed duration: {selected_videos_duration}s")
        # Set the paths of the selected files
        video_paths = [os.path.join(video_folder, file) for file in selected_video_files]

    # Get all song file names in the specified folder
    songs = [song for song in os.listdir(song_folder) if song.endswith(".mp3")]

    if is_tiktok_content:
        songs = video_files

    if not songs:
        st.error("The folder doesn't contain any songs")
        selected_song = None
    else:
        st.toast("Selecting a song...")
        st.write("Selecting a song...")

        # Randomly select a song
        selected_song = random.choice(songs)

        song_duration = AudioFileClip(os.path.join(song_folder, selected_song)).duration

        while song_duration < duration_length:
            st.toast(f"Selected a {song_duration}s long song, reselecting to match desired duration {duration_length}s...", icon="🏃")
            st.write(f"Selected a {song_duration}s long song, reselecting to match desired duration {duration_length}s...")

            # Randomly select a song
            selected_song = random.choice(songs)
            song_duration = AudioFileClip(os.path.join(song_folder, selected_song)).duration

        st.write(f"Verified! Selected a {song_duration}s long song, Desired duration: {duration_length}s")
        selected_song_path = os.path.join(song_folder, selected_song)

    overlay_path = None

    if overlay_folder is not None:
        # Get all image files in the specified overlay folder
        overlay_files = [file for file in os.listdir(overlay_folder) if file.endswith((".png", ".jpg", ".jpeg"))]

        if overlay_files:
            st.write("Selecting an overlay...")
            # Randomly select an overlay image
            overlay_file = random.choice(overlay_files)
            overlay_path = os.path.join(overlay_folder, overlay_file)
            st.write("Done with the overlay!")

        else:
            st.error("The folder doesn't contain any overlays")

    return video_paths, selected_song_path, overlay_path
