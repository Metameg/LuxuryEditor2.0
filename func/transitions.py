import os
import subprocess
import pathlib
import ffmpeg
import random
import streamlit as st
from func.randomize import randomize_files


def _get_random_transition():
    transitions = ['fade', 'wipeleft', 'wiperight','wipeup','wipedown','slideleft','slideright','slideup',
        'slidedown','circlecrop','rectcrop','distance','fadeblack','fadewhite','radial','smoothleft','smoothup','smoothdown',
        'circleopen','circleclose','vertopen','vertclose','horzopen','horzclose','dissolve','pixelize','diagtl','diagtr',
        'diagbl','diagbr','hlslice','hrslice','vuslice','vdslice','hblur','fadegrays','wipetl','wipetr','wipebl','wipebr',
        'squeezeh','squeezev','zoomin','fadefast','fadeslow','hrwind','vuwind','vdwind','coverleft','coverright',
        'coverup','coverdown','revealleft','revealright','revealup','revealdown'
    ]

    return random.choice(transitions)

def create_transition_segment(clip1, clip2, duration, clip_duration, idx):
    output_file = os.path.join(pathlib.Path(__file__).parent.absolute(), 'temp', f'transition{idx}.mp4')

    transition = _get_random_transition()

    ffmpeg_command = [
    'ffmpeg',
    '-i', clip1,
    '-i', clip2,
    '-filter_complex',
    f'[0]settb=AVTB,fps=30[v0];[1]settb=AVTB,fps=30[v1];[v0][v1]xfade=transition={transition}:duration={duration}:offset={clip_duration - duration},format=yuv420p',
    output_file
    ]

    subprocess.run(ffmpeg_command)

    return output_file


def ffmpeg_video_collage(video_folder, num_videos, song_folder, overlay_folder, export_folder, videos_count, duration_length, is_tiktok_content):
    final_video =  os.path.join(os.getcwd(), 'output', 'final_video.mp4')

    with st.status("Selecting media..."):
        video_files, selected_song, overlay_path = randomize_files(video_folder, num_videos, song_folder, overlay_folder, duration_length, is_tiktok_content)

    clips = video_files

    # Calculate the duration for each video clip
    duration = duration_length / num_videos
    
    input_streams = []
    print(len(clips))
    for i, clip in enumerate(clips):
        
        probe = ffmpeg.probe(clip, show_entries='format=duration')
        clip_duration = float(probe['format']['duration'])

        clip_duration = min(clip_duration, duration)  # Use the minimum between clip duration and desired duration
        
        if (i > 0):
            print("clip1:", clips[i-1])
            print("clip2:", clips[i])
            transition_segment = create_transition_segment(clips[i-1], clips[i], 0.5, clip_duration, i)

            if (i == len(clips) - 1):
                clip_duration *= 2
            
            input_stream = ffmpeg.input(transition_segment, ss=0, t=clip_duration)
            input_streams.append(input_stream)
    
    video = ffmpeg.concat(*input_streams, v=1, a=0)    
    audio = ffmpeg.input(selected_song, ss=0, t=duration_length)    
    output_options = {
                    'c:v': 'libx264',
                    'hide_banner': None,
                    'loglevel': 'error'
        }
    ffmpeg.output(video, audio, final_video, **output_options).run(overwrite_output=True)

    # Clean up temp file
    transitions = os.listdir(os.path.join(pathlib.Path(__file__).parent.absolute(), 'temp'))
    for transition in transitions:
        os.remove(os.path.join(pathlib.Path(__file__).parent.absolute(), 'temp', transition))

# gK7bxrXpSpdXsJ4zxPHwJg1p66qcaPhA.mp4        