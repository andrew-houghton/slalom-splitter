from pathlib import Path

from moviepy.editor import ColorClip, VideoFileClip, clips_array

clip1 = (
    "/home/andrew/personal/slalom-splitter/clips/2022-12-12 Bradys slalom/GH010708.MP4"
)
clip2 = (
    "/home/andrew/personal/slalom-splitter/clips/2022-12-12 Bradys slalom/GH010709.MP4"
)

vid1 = VideoFileClip(clip1, audio=True).subclip(0, 10)
vid2 = VideoFileClip(clip2, audio=False).subclip(0, 10)

blank = ColorClip(vid1.size, (0, 0, 0), duration=10)

clips_array = clips_array([[vid1, vid2], [vid1, blank]])
clips_array.write_videofile("clips/poc.mp4")
