import streamlit as st
import os
import shutil
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip
import time
from datetime import datetime
import random
from func.randomize import randomize_files
from proglog import ProgressBarLogger
from func.req import save_json, open_json

class MyBarLogger(ProgressBarLogger):
    def __init__(self):
        super().__init__()
        self.percentage = 0  # Initialize percentage
        self.progress_bar = st.progress(0)  # Create progress bar

    def bars_callback(self, bar, attr, value, old_value=None):
        # Every time the logger progress is updated, this function is called
        self.percentage = (value / self.bars[bar]['total']) * 100
        self.progress_bar.progress(self.percentage / 100)

FPS = 24
exporting_paths_database = "exporting_paths.txt"

# Check if exporting_paths.txt exists, if not, create it
if not os.path.exists(exporting_paths_database):
    with open(exporting_paths_database, "w") as file:
        pass

def create_video_collage(video_folder, num_videos, song_folder, overlay_folder, export_folder, videos_count, duration_length, is_tiktok_content):
    # Calculate the duration for each video clip
    duration = duration_length / num_videos

    duration_taken = 0
    average_exporting_speed = 0
 
    for i in range(videos_count):
        video_counter = "st" if i+1 == 1 else "nd" if i+1 == 2 else "rd" if i+1 == 3 else "th"
        video_counter = str(i+1) + video_counter + " Video"

        st.subheader(video_counter)

        with st.status("Selecting media..."):
            video_files, selected_song, overlay_path = randomize_files(video_folder, num_videos, song_folder, overlay_folder, duration_length, is_tiktok_content)

        if video_files is None:
            st.error("The directory does not contain any videos")
        elif selected_song is None:
            st.error("The directory does not contain any songs")
        else:
            with st.status("Loading media..."):
                for video_file in video_files:
                    st.video(video_file)

                if overlay_path is not None:
                    # Get the script directory
                    script_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), overlay_folder)
                    overlay_filename = os.path.basename(overlay_path)

                    # Create the destination path in the script directory
                    destination_path = os.path.join(script_directory, overlay_filename)

                    try:
                        # Copy the image to the script directory
                        shutil.copy2(overlay_path, destination_path)
                        st.subheader("Selected Overlay")
                        st.image(f"overlays/{overlay_filename}", caption="Watermark", use_column_width=True)
                    except FileNotFoundError:
                        print("Error: The specified image file does not exist.")
                    except PermissionError:
                        print("Error: Permission denied. Unable to copy the image.")

                st.subheader("Selected Song")
                st.audio(selected_song)
    
            with st.status("Editing video..."):
                # Randomly select the videos
                selected_videos = random.sample(video_files, num_videos)

                output_width, output_height = 1080, 1920  # Replace with the desired output dimensions

                # Initialize an array to store video clips
                video_clips = []
                clip_durations = []
                
                # Iterate over each selected video and extract the desired duration
                for video in selected_videos:
                    video_path = os.path.join(video_folder, video)
                    clip = VideoFileClip(video_path)
                    clip_duration = min(clip.duration, duration)  # Use the minimum between clip duration and desired duration
                    # Resize the clip if it's smaller than the output dimensions
                    try:
                        if clip.size[0] < output_width or clip.size[1] < output_height:
                            clip = clip.resize((output_width, output_height))
                    except Exception as e:
                        st.error(f'Fix the problem with {video}.\n Due to error {str(e)}')
                        

                    clip = clip.subclip(0, clip_duration)
                    # if clip.fps == FPS:
                    video_clips.append(clip)
                    clip_durations.append(clip_duration)

                st.write("Making Luxury...")

                # Concatenate the video clips horizontally to create a collage
                final_clip = concatenate_videoclips(video_clips, method="compose")

                # Set the audio of the final clip as the selected song
                song_path = os.path.join(song_folder, selected_song)
                audio = AudioFileClip(song_path)
                
                # Cut the audio based on the total duration of the video clips
                total_duration = sum(clip_durations)
                audio = audio.subclip(0, total_duration)
                final_clip = final_clip.set_audio(audio)

                if overlay_path is not None:
                    st.toast("Adding watermark...")
                    st.write("Adding watermark...")

                    try:
                        # Add image overlay
                        overlay = ImageClip(overlay_path)
                        
                        overlay = overlay.resize(height=final_clip.h // 10)  # Resize the overlay to half the height of the video
                        overlay = overlay.set_duration(final_clip.duration)
                        overlay = overlay.set_position(("center", "center"))  # Set overlay position to center and top
                        final_clip = CompositeVideoClip([final_clip, overlay])

                        overlay.close()
                    except Exception as e:
                        st.error(f"Failed to add watermark due to {str(e)}")

                # Define the output file path with the correct file extension in the export folder
                output_path = os.path.join(export_folder, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mp4")

                st.toast(f"Editing {video_counter}...", icon="🏃")
                st.write(f"Editing {video_counter}...")

                logger = MyBarLogger()

                start_time = time.time()

                # Write the final clip to the output file with a specified FPS value
                final_clip.write_videofile(output_path, preset="ultrafast", codec="libx264", fps=FPS, audio_codec="aac", logger=logger)

                data = open_json()

                data["export"]["exported_videos"].append(output_path)

                save_json(data)

                end_time = time.time()

                time_difference = end_time - start_time
                
                st.toast(f"This {video_counter} export took {int(time_difference)} seconds to export", icon="🚀")
                st.write(f"This {video_counter} export took {int(time_difference)} seconds to export")

                duration_taken += time_difference

                average_exporting_speed = (i+1) * 3600 / duration_taken

                st.success(f"Luxury Clips Created Successfully! With the speed {int(average_exporting_speed)} videos/hour.")

                if logger.percentage == 100:
                    st.video(output_path)