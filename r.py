import yt_dlp, random, os, sys, shutil, subprocess, textwrap, re, json
from datetime import datetime
from yt_dlp.postprocessor.sponsorblock import SponsorBlockPP

# Output width
outw = 1920
# Output height
outh = 1080

def main():
    if not os.path.exists('intro.mp4'):
        sys.exit('intro.mp4 file is missing')

    if not os.path.exists('doorbell.wav'):
        sys.exit('doorbell.wav file is missing')

    with open('list.txt') as list:
        vids = []
        for line in list:
            vids.append(line.rstrip())

    if len(vids) < 60:
        sys.exit('list.txt must contain 60 or more URLs on separate lines')

    if not os.path.isdir('temp'):
        os.mkdir('temp')
        os.mkdir('temp/conv')

    with open('temp/files.txt', 'w') as f:
        f.write('file \'conv/intro.mp4\'')
        for x in range(60):
            f.write('\nfile \'conv/' + str(x+1) + '.mp4\'')

    q = 'ultrafast'
    if (len(sys.argv) > 1):
        q = sys.argv[1]

    loudness = loud('intro.mp4')
    if 'inf' in loudness['input_i'] or 'inf' in loudness['input_tp'] or 'inf' in loudness['target_offset']:
        os.system('ffmpeg -hide_banner -i intro.mp4 -c:v libx264 -profile:v baseline -level:v 4.0 -crf 18 -preset ' + q + ' -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -vf \"scale=(iw*sar)*min(' + str(outw) + '/(iw*sar)\\,' + str(outh) + '/ih):ih*min(' + str(outw) + '/(iw*sar)\\,' + str(outh) + '/ih), pad=' + str(outw) + ':' + str(outh) + ':(' + str(outw) + '-iw*min(' + str(outw) + '/iw\\,' + str(outh) + '/ih))/2:(' + str(outh) + '-ih*min(' + str(outw) + '/iw\\,' + str(outh) + '/ih))/2, fps=23.976\" temp/conv/intro.mp4')
    else:
        os.system('ffmpeg -hide_banner -i intro.mp4 -c:v libx264 -profile:v baseline -level:v 4.0 -crf 18 -preset ' + q + ' -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -vf \"scale=(iw*sar)*min(' + str(outw) + '/(iw*sar)\\,' + str(outh) + '/ih):ih*min(' + str(outw) + '/(iw*sar)\\,' + str(outh) + '/ih), pad=' + str(outw) + ':' + str(outh) + ':(' + str(outw) + '-iw*min(' + str(outw) + '/iw\\,' + str(outh) + '/ih))/2:(' + str(outh) + '-ih*min(' + str(outw) + '/iw\\,' + str(outh) + '/ih))/2, fps=23.976\" -af loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=' + loudness['input_i'] + ':measured_LRA=' + loudness['input_lra'] + ':measured_TP=' + loudness['input_tp'] + ':measured_thresh=' + loudness['input_thresh'] + ':offset=' + loudness['target_offset'] + ':linear=true:print_format=summary temp/conv/intro.mp4')

    loudness = loud('doorbell.wav')
    os.system('ffmpeg -hide_banner -i doorbell.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=' + loudness['input_i'] + ':measured_LRA=' + loudness['input_lra'] + ':measured_TP=' + loudness['input_tp'] + ':measured_thresh=' + loudness['input_thresh'] + ':offset=' + loudness['target_offset'] + ':linear=true:print_format=summary temp/conv/doorbell.wav')

    dur = 0.0
    for i in range(1, 61):
        ydl_opts = {
            'format': 'bv[vcodec!=vp9]+ba',
            'merge_output_format': 'mkv',
            'outtmpl': 'temp/orig/' + str(i),
            'ignoreerrors': 'True',
            'postprocessors': [{
                'key': 'SponsorBlock',
                'when': 'pre_process'
            },
            {
                'key': 'ModifyChapters',
                'force_keyframes': 'True',
                'remove_sponsor_segments': SponsorBlockPP.CATEGORIES.keys(),
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            vidinfo = ydl.extract_info(vids.pop(random.randint(0, len(vids) - 1)), download=True)
        with open('temp/title.txt', 'w') as title:
            title.write(textwrap.fill(re.sub('(?i)\s*[\[\{\(][^[\[\{\(]*(official|version|edited|video|explicit).*[\]\}\)]', '', vidinfo['title']), width=65))
        dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 'temp/orig/' + str(i) + '.mkv']))
        start = random.uniform(0, dur - 60)
        loudness = loud('temp/orig/' + str(i) + '.mkv', start, True)
        crop_results = subprocess.Popen(['ffmpeg -hide_banner -ss ' + str(start) + ' -i temp/orig/' + str(i) + '.mkv -vf cropdetect=24:1:0 -t 60 -f null - 2>&1 | awk \'/crop/ { print $NF }\' | tail -1'], shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.read().strip()[5:]
        dim = crop_results.split(':')
        os.system('ffmpeg -hide_banner -ss ' + str(start) + ' -i temp/orig/' + str(i) + '.mkv -i temp/conv/doorbell.wav -c:v libx264 -profile:v baseline -level:v 4.0 -crf 18 -preset ' + q + ' -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -vf \"scale=(iw*sar)*min(' + str(outw) + '/(' + dim[0] + '*sar)\\,' + str(outh) + '/' + dim[1] + '):ih*min(' + str(outw) + '/(' + dim[0] + '*sar)\\,' + str(outh) + '/' + dim[1] + '), crop=min(' + str(outw) + '\\,iw):min(' + str(outh) + '\\,ih), pad=' + str(outw) + ':' + str(outh) + ':(' + str(outw) + '-iw*min(' + str(outw) + '/iw\\,' + str(outh) + '/ih))/2:(' + str(outh) + '-ih*min(' + str(outw) + '/iw\\,' + str(outh) + '/ih))/2, fps=23.976, drawtext=textfile=temp/title.txt:fontfile=titlefont.ttf:alpha=\'if(lt(t,3),0,if(lt(t,4),(t-3)/1,if(lt(t,11),1,if(lt(t,12),(1-(t-11))/1,0))))\':x=(w-text_w)/2:y=' + str(outh * 0.8) + ':fontsize=' + str(outh * 0.042) + ':fontcolor=0x212121:box=1:boxcolor=0xffffff@0.85:boxborderw=' + str(outh * 0.014) + '\" -filter_complex [0:a]loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=' + loudness['input_i'] + ':measured_LRA=' + loudness['input_lra'] + ':measured_TP=' + loudness['input_tp'] + ':measured_thresh=' + loudness['input_thresh'] + ':offset=' + loudness['target_offset'] + ':linear=true:print_format=summary[a1],[a1][1:a]amix=dropout_transition=0:normalize=false[a2] -t 60 -map 0:v -map \"[a2]\" temp/conv/' + str(i) + '.mp4')
        os.remove('temp/orig/' + str(i) + '.mkv')

    endtime = datetime.now().isoformat()
    os.system('ffmpeg -hide_banner -f concat -safe 0 -i temp/files.txt -c copy \"' + endtime[:13] + endtime[14:16] + ' PH.mp4\"')
    shutil.rmtree('temp')
    print('Video was successfully generated!')

def loud(file, start = 0, mv = False):
    if mv:
        data = subprocess.run(['ffmpeg', '-hide_banner', '-ss', str(start), '-i', file, '-vn', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-t', '60', '-f', 'null', '-'], stderr=subprocess.PIPE).stderr.decode('utf-8')
    else:
        data = subprocess.run(['ffmpeg', '-hide_banner', '-i', file, '-vn', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], stderr=subprocess.PIPE).stderr.decode('utf-8')
    loudness = json.loads('{' + data.split('{')[1].split('}')[0] + '}')
    return loudness

if __name__ == "__main__":
    main()
