import os
import pathlib
import ffmpeg
import random


def _get_random_transition():
    transitions = ['fade', 'wipeleft', 'wiperight','wipeup','wipedown','slideleft','slideright''slideup',
        'slidedown','circlecrop','rectcrop','distance','fadeblack','fadewhite','radial','smoothleft','smoothup','smoothdown',
        'circleopen','circleclose','vertopen','vertclose','horzopen','horzclose','dissolve','pixelize','diagtl','diagtr',
        'diagbl','diagbr','hlslice','hrslice','vuslice','vdslice','hblur','fadegrays','wipetl','wipetr','wipebl','wipebr',
        'squeezeh','squeezev','zoomin','fadefast','fadeslow','hrwind','vuwind','vdwind','coverleft','coverright',
        'coverup','coverdown','revealleft','revealright','revealup','revealdown'
    ]

    return random.choice(transitions)

def add_transition(clip1, clip2, duration):
    temp_path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'temp', 'out.mp4')
    if not os.path.isfile(temp_path):
        print("here")
        with open(temp_path, 'w') as fp:
            pass
    
    # Get duration of first clip
    ffmpeg.output(clip1, temp_path).run(overwrite_output=True)
    probe = ffmpeg.probe(temp_path, show_entries='format=duration')
    clip_duration = float(probe['format']['duration'])
    os.remove(temp_path)
   
    
    print("there")
    transition = _get_random_transition()
    output_options = {
        'filter_complex': f'xfade=transition={transition}:duration={duration}:offset={clip_duration - duration}'
    }

    ffmpeg.output(clip1, clip2, output_file, **output_options).run(overwrite_output=True)
    

if __name__ == '__main__':
    
    input_file = 'segment_3.mp4'
    output_file = 'output_ffmpeg.mp4'

    # Input video stream
    input_video = ffmpeg.input(input_file)
    
    segment_duration = 3
    input_streams = []
    for i in range(2):
        start_time = i * segment_duration

        input_stream = ffmpeg.input(input_file, ss=start_time, t=3)
        print(input_stream)
        input_streams.append(input_stream)

        if (i > 0):
            add_transition(input_streams[i-1], input_streams[i], 1)
            


