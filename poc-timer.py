import gizeh
from moviepy.editor import *

duration = 5
video = VideoFileClip("clips/2022-12-12 Bradys slalom/GH010708.MP4").subclip(
    50, 50 + duration
)


def make_frame(t):
    surface = gizeh.Surface(128, 128)  # width, height
    text = gizeh.text(
        str(round(t, 1)), fontfamily="Impact", fontsize=40, fill=(1, 1, 1), xy=(64, 64)
    )
    text.draw(surface)
    return surface.get_npimage(transparent=True)  # returns a 8-bit RGB array


countdown_mask = VideoClip(
    lambda t: make_frame(t)[:, :, 3] / 255.0, duration=duration, ismask=True
)
countdown = VideoClip(lambda t: make_frame(t)[:, :, :3], duration=duration).set_mask(
    countdown_mask
)
countdown = countdown.set_position((100,100))
result = CompositeVideoClip([video, countdown])
result.write_videofile("clips/poc-timer.mp4")
