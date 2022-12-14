import json
import gizeh
from pathlib import Path
import sys
from pprint import pprint
from moviepy.editor import ColorClip, VideoFileClip, VideoClip, CompositeVideoClip
import time
import numpy as np


def clips_array(array, other_clips):
    array = np.array(array)
    sizes_array = np.array([[clip.size for clip in line] for line in array])

    # find row width and col_widths automatically if not provided
    rows_widths = sizes_array[:, :, 1].max(axis=1)
    cols_heights = sizes_array[:, :, 0].max(axis=0)

    # compute start positions of X for rows and Y for columns
    xs = np.cumsum([0] + list(cols_heights))
    ys = np.cumsum([0] + list(rows_widths))

    # position clips
    for j, (x, ch) in enumerate(zip(xs[:-1], cols_heights)):
        for i, (y, rw) in enumerate(zip(ys[:-1], rows_widths)):
            array[i, j] = array[i, j].set_position((x, y))

    # add other clips
    clips = list(array.flatten()) + other_clips
    return CompositeVideoClip(clips, size=(xs[-1], ys[-1]), bg_color=None)


assert Path(sys.argv[1]).exists(), "Splits file be passed in as argument"
assert sys.argv[1].endswith('.json'), "Splits file be a json file"

def parse_splits_string(value):
    output = []
    for row in value.split("\n"):
        items = row.split(" - ")
        time = float(items[1].replace('s', ''))
        penalty = None
        if len(items) == 3:
            penalty = float(items[2].replace('s', '').replace('+', ''))
        output.append((time, penalty))
    return output

with open(Path(sys.argv[1]), "r") as handle:
    data = json.load(handle)
    data = {k: parse_splits_string(v)[:8] for k,v in data.items()}

def calculate_run_duration(parsed_splits):
    # Ignore penalties
    return parsed_splits[-1][0] + parsed_splits[0][0]

run_durations = {k: calculate_run_duration(v) for k,v in data.items()}
runs_by_speed = sorted(run_durations, key=lambda file: run_durations[file])

def load_clip_with_buffer(file, start, end, buffer=2):
    return VideoFileClip(file).subclip(start-buffer, end).resize(0.5)


clips = [load_clip_with_buffer(file, data[file][0][0], data[file][-1][0]) for file in runs_by_speed]
for i in range(1, len(clips)):
    clips[i]= clips[i].without_audio()

blank = ColorClip(clips[0].size, (0, 0, 0), duration=clips[-1].duration)
clips_grid = [clips[0:3], [clips[3], clips[4], blank]]

total_height = len(clips_grid)*clips[0].size[1]
total_width = len(clips_grid[0])*clips[0].size[0]
print(total_height, total_width)

# TODO
# setup main timer in the top middle
# add an overall split timer to clips
# add a gate split timer to clips

def make_timer(t):
    surface = gizeh.Surface(height=total_height, width=total_width)
    real_time = t - 2
    text = gizeh.text(
        str(round(t - 2, 1)) + 's',
        fontfamily="Impact",
        fontsize=60,
        fill=(1, 1, 1),
        xy=(total_width/2, 64),
    )
    text.draw(surface)

    # For clips[1]
    if real_time > 0:
        position = (0, 1)
        splits = data[runs_by_speed[1]]
        splits = [i[0] - splits[0][0] for i in splits]
        fastest_splits = data[runs_by_speed[0]]
        fastest_splits = [i[0] - fastest_splits[0][0] for i in fastest_splits]

        last_gate_completed = 0
        for i in range(len(splits)):
            if real_time > splits[i]:
                last_gate_completed = i
            else:
                break

        time_last_gate = splits[last_gate_completed]
        fastest_last_gate = fastest_splits[last_gate_completed]
        overall_split_time = time_last_gate - fastest_last_gate

        overall_split_text = gizeh.text(
            str(round(overall_split_time, 1)) + 's',
            fontfamily="Impact",
            fontsize=40,
            fill=(1, 1, 1),
            xy=(
                position[1] * clips[0].size[0] + clips[0].size[0] * 0.5,
                (1 + position[0]) * clips[0].size[1] - 192,
            ),
        )
        overall_split_text.draw(surface)

    return surface.get_npimage(transparent=True)  # returns a 8-bit RGB array

total_duration = max(i.duration for i in clips)
countdown_mask = VideoClip(lambda t: make_timer(t)[:, :, 3] / 255.0, duration=total_duration, ismask=True)
countdown = VideoClip(lambda t: make_timer(t)[:, :, :3], duration=total_duration).set_mask(countdown_mask)

joined_clips = clips_array(clips_grid, [countdown])
start = time.perf_counter()
joined_clips.write_videofile("clips/output.mp4", fps=30)
print(f"finished writing video in {time.perf_counter() - start:.1f}s")
