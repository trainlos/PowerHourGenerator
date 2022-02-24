## DEPENDENCIES
- [FFmpeg 4.4+](https://www.ffmpeg.org/)
- [Python 3.6+](https://www.python.org/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## HOW TO RUN
`python3 r.py`

list.txt must contain 60 or more URLs each on a separate line. Currently only YouTube URLs are supported. This script does not perform any URL sanitization so please sanitize your URLs to decrease the chances of parsing errors. Both full and shortened YouTube URLs are accepted. Here are some examples of properly formatted URLs:
> https://youtu.be/jNQXAC9IVRw
>
> https://www.youtube.com/watch?v=jNQXAC9IVRw

## FILE REPLACEMENTS
The default files this script looks for are:

 - intro.mp4
 - outro.mp4
 - doorbell.wav
 - titlefont.ttf

The included files can be replaced by any other valid file. Just delete (or rename) the included file and copy your new file in place of it with the appropriate filename. Alternatively, you can use the arguments listed below to specify a file with a different location or extension.

`-i, --intro PATH`

`-o, --outro PATH`

`-d, --doorbell PATH`

`-t, --font PATH`

The intro and outro files are optional, but a doorbell file is required. If the font file is missing and FFmpeg was configured with `--enable-libfontconfig` then the system default sans font will be used instead.

## ADDITIONAL ARGUMENTS
`-p, --preset PRESET`

  All presets will output the same quality, but a slower preset will achieve a smaller filesize.

  [List of available presets:](https://trac.ffmpeg.org/attachment/wiki/Encode/H.264/encoding_time.png)
  - ultrafast *(default)*
  - superfast
  - veryfast
  - faster
  - fast
  - medium
  - slow
  - slower
  - veryslow

`-f, --fps FLOAT`

  Sets the framerate of the output video. Default is 23.976.

`-v, --vfr INT`

  Video sync method

  - 0 *(default)*: Output video will be encoded at the constant framerate provided by `--fps`.
  - 1: Output video will attempt to retain the different framerates of the input videos. `--fps` is ignored when this option is selected. May have A/V sync issues on some hardware / video players.

`-w, --outw INT`

  Sets the width of the output video. Default is 1920.

`-h, --outh INT`

  Sets the height of the output video. Default is 1080.



### Examples
Prioritizing a smaller output file size over speed:

`python3 r.py --preset veryslow`

Scaling the output video to the screen resolution of the iPhone 13 with variable framerate:

`python3 r.py --outh 1170 --outw 2532 --vfr 1`

Outputting a 320x240 video with a framerate of 15 fps:

`python3 r.py --outw 320 --outh 240 --fps 15`

## TROUBLESHOOTING
If anything goes wrong that causes the script to stop before the end just delete the entire 'temp' folder to reset everything to a clean starting position.

YouTube doesn't properly encode their VP9 videos. [FFmpeg just added a fix for this on 2022-02-13](http://git.videolan.org/?p=ffmpeg.git;a=commitdiff;h=68595b46cb374658432fff998e82e5ff434557ac) so until there is a new major release of FFmpeg with the patch included this power hour script will retain the logic to ignore VP9 streams. This may result in downloaded videos occasionally having reduced quality compared to the version you see on YouTube.

## TODO
- Optimize non-music removal step to solve desync issues without drastically increasing render time.
