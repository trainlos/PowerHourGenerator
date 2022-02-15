# DEPENDENCIES
- [FFmpeg 4.4+](https://www.ffmpeg.org/)
- [Python 3.6+](https://www.python.org/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

On Ubuntu these can be installed with:

`sudo apt -y install ffmpeg python3 yt-dlp`

# HOW TO RUN
`python3 r.py`

'list.txt' must contain 60 or more URLs each on a separate line. Currently only YouTube URLs are supported. This script does not perform any URL sanitization so please sanitize your URLs to decrease the chances of parsing errors. Both full and shortened YouTube URLs are accepted. Here are some examples of properly formated URLs:
> https://youtu.be/jNQXAC9IVRw
> 
> https://www.youtube.com/watch?v=jNQXAC9IVRw

# OPTIONAL ARGUMENTS
By default this script runs with the 'ultrafast' preset which runs the fastest at the expense of quality and storage space. This can be changed by supplying the preferred preset as an argument. For example, this would generate the smallest and highest quality video file.

`python3 r.py veryslow`

[Full list of available presets:](https://trac.ffmpeg.org/attachment/wiki/Encode/H.264/encoding_time.png)
- ultrafast (default)
- superfast
- veryfast
- faster
- fast
- medium
- slow
- slower
- veryslow

# FILE REPLACEMENTS
'intro.mp4' can be replaced by any .mp4 file. Just delete (or rename) the included 'intro.mp4' file and then copy your new intro in place of it. Make sure the new file has the correct filename of 'intro.mp4'. Similarly, 'doorbell.wav' can be replaced by another .wav file. 'titlefont.ttf' can be replaced by any other .ttf file. If this file is missing and FFmpeg was configured with `--enable-libfontconfig` then the system default sans font will be used instead.

# TROUBLESHOOTING
If anything goes wrong that causes the script to stop before the end just delete the entire 'temp' folder to reset everything to a clean starting position.

There's a bug with YouTube's VP9 encoding that causes videos to be broken. [FFmpeg just added a fix for this on 2022-02-13](http://git.videolan.org/?p=ffmpeg.git;a=commitdiff;h=68595b46cb374658432fff998e82e5ff434557ac) so until this patch more widely available in prebuilt versions of FFmpeg, this PH generator will retain the logic to ignore VP9 streams. This may result in downloaded videos occasionally having noticeably reduced quality compared to the version you see on YouTube.

# TODO
- Add option to choose between VFR and CFR (only VFR supported at the moment)
- Add option to choose different output resolution at runtime
- Optimize non-music removal step so videos aren't transcoded twice
