import yt_dlp, random, os, sys, shutil, subprocess, textwrap, re, json, argparse
from datetime import datetime
from yt_dlp.postprocessor.sponsorblock import SponsorBlockPP

def main():
    parser = argparse.ArgumentParser(add_help = False)
    parser.add_argument('-p', '--preset', type = str, choices = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow', 'placebo'], default='ultrafast')
    parser.add_argument('-f', '--fps', type = float, default = 24000/1001)
    parser.add_argument('-v', '--vfr', type = int, default = 0)
    parser.add_argument('-w', '--outw', type = int, default = 1920)
    parser.add_argument('-h', '--outh', type = int, default = 1080)
    parser.add_argument('-i', '--intro',  type=str)
    parser.add_argument('-o', '--outro',  type=str)
    parser.add_argument('-d', '--doorbell', type=str)
    parser.add_argument('-t', '--font', type=str)
    main.args = parser.parse_args()

    with open('list.txt', 'a+') as list:
        list.seek(0)
        vids = []
        for line in list:
            vids.append(line.rstrip())

    if len(vids) < 60:
        sys.exit('list.txt must contain 60 or more URLs on separate lines.')

    def input_check(argin, defin, req = False):
        if argin:
            if not os.path.exists(argin):
                if os.path.exists(defin):
                    proceed = input(argin + ' cannot be found. \nWould you like to use ' + defin + ' instead? [y/n] ')
                    if proceed.lower() == 'y' or proceed.lower() == 'yes':
                        argin = defin
                    else:
                        sys.exit('Abort.')
                else:
                    sys.exit(argin + ' cannot be found.')
        else:
            if not os.path.exists(defin):
                if req:
                    sys.exit(defin + ' cannot be found.')
                else:
                    proceed = input(defin + ' cannot be found. \nWould you like to proceed without it? [y/n] ')
                    if proceed.lower() != 'y' and proceed.lower() != 'yes':
                        sys.exit('Abort.')
            else:
                argin = defin

    input_check(main.args.intro, 'intro.mp4')
    input_check(main.args.outro, 'outro.mp4')
    input_check(main.args.doorbell, 'doorbell.wav', True)

    if main.args.font:
        if not os.path.exists(main.args.font):
            if os.path.exists('titlefont.ttf'):
                proceed = input(main.args.font + ' cannot be found. \nWould you like to use titlefont.ttf instead? [y/n] ')
                if proceed.lower() == 'y' or proceed.lower() == 'yes':
                    main.args.font = 'titlefont.ttf'
                else:
                    sys.exit('Abort.')
    else:
        main.args.font = 'titlefont.ttf'

    if not os.path.isdir('temp'):
        os.mkdir('temp')
        os.mkdir('temp/conv')

    with open('temp/files.txt', 'w') as f:
        if main.args.intro:
            f.write('file \'conv/intro.mp4\'')
            subprocess.run(buildFFmpegCommand(main.args.intro, 'temp/conv/intro.mp4'))
        for x in range(60):
            f.write('\nfile \'conv/' + str(x+1) + '.mp4\'')
        if main.args.outro:
            f.write('file \'conv/outro.mp4\'')
            subprocess.run(buildFFmpegCommand(main.args.outro, 'temp/conv/outro.mp4'))

    loudness = loud(main.args.doorbell)
    subprocess.run(['ffmpeg', '-hide_banner', '-i', main.args.doorbell, '-c:a', 'pcm_s16le', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=' + loudness['input_i'] + ':measured_LRA=' + loudness['input_lra'] + ':measured_TP=' + loudness['input_tp'] + ':measured_thresh=' + loudness['input_thresh'] + ':offset=' + loudness['target_offset'] + ':linear=true:print_format=summary', 'temp/conv/doorbell.wav'])

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
        if i == 60:
            crop_results = subprocess.Popen(['ffmpeg -hide_banner -i temp/orig/' + str(i) + '.mkv -vf cropdetect=24:1:0 -f null - 2>&1 | awk \'/crop/ { print $NF }\' | tail -1'], shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.read().strip()[5:]
            main.dim = crop_results.split(':')
            subprocess.run(buildFFmpegCommand('temp/orig/60.mkv', 'temp/conv/60.mp4'))
        else:
            crop_results = subprocess.Popen(['ffmpeg -hide_banner -ss ' + str(start) + ' -i temp/orig/' + str(i) + '.mkv -vf cropdetect=24:1:0 -t 60 -f null - 2>&1 | awk \'/crop/ { print $NF }\' | tail -1'], shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.read().strip()[5:]
            main.dim = crop_results.split(':')
            subprocess.run(buildFFmpegCommand('temp/orig/' + str(i) + '.mkv', 'temp/conv/' + str(i) + '.mp4', True, start))
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
    print(data)
    loudness = json.loads('{' + data.split('{')[1].split('}')[0] + '}')
    return loudness

def buildFFmpegCommand(fin, fout, mv = False, start = 0):
    loudness = loud(fin, start, mv)
    scale = 'scale=(iw*sar)*min(' + str(main.args.outw) + '/(iw*sar)\\,' + str(main.args.outh) + '/ih):ih*min(' + str(main.args.outw) + '/(iw*sar)\\,' + str(main.args.outh) + '/ih)'
    pad = 'pad=' + str(main.args.outw) + ':' + str(main.args.outh) + ':(' + str(main.args.outw) + '-iw*min(' + str(main.args.outw) + '/iw\\,' + str(main.args.outh) + '/ih))/2:(' + str(main.args.outh) + '-ih*min(' + str(main.args.outw) + '/iw\\,' + str(main.args.outh) + '/ih))/2'
    drawtext = ''

    if mv:
        commands = ['ffmpeg', '-hide_banner', '-ss', str(start), '-i', fin, '-i', 'temp/conv/doorbell.wav']
        scale = 'scale=(iw*sar)*min(' + str(main.args.outw) + '/(' + main.dim[0] + '*sar)\\,' + str(main.args.outh) + '/' + main.dim[1] + '):ih*min(' + str(main.args.outw) + '/(' + main.dim[0] + '*sar)\\,' + str(main.args.outh) + '/' + main.dim[1] + '), crop=min(' + str(main.args.outw) + '\\,iw):min(' + str(main.args.outh) + '\\,ih)'
        drawtext = ', drawtext=textfile=temp/title.txt:fontfile=' + main.args.font + ':alpha=\'if(lt(t,3),0,if(lt(t,4),(t-3)/1,if(lt(t,11),1,if(lt(t,12),(1-(t-11))/1,0))))\':x=(w-text_w)/2:y=' + str(main.args.outh * 0.8) + ':fontsize=' + str(main.args.outh * 0.042) + ':fontcolor=0x212121:box=1:boxcolor=0xffffff@0.85:boxborderw=' + str(main.args.outh * 0.014)
    else:
        commands = ['ffmpeg', '-hide_banner', '-i', fin]

    commands += [
        '-c:v',
        'libx264',
        '-profile:v',
        'baseline',
        '-level:v',
        '4.0',
        '-crf',
        '18',
        '-preset',
        main.args.preset,
        '-pix_fmt',
        'yuv420p',
        '-c:a',
        'aac',
        '-b:a',
        '256k',
        '-ar',
        '48000',
        '-ac',
        '2'
    ]

    if main.args.vfr:
        commands += ['-vsync', 'vfr', '-video_track_timescale', '90k', '-vf', scale + ',' + pad + drawtext]
    else:
        commands += ['-vf', scale + ',' + pad + ',fps=' + str(main.args.fps) + drawtext]

    if loudness:
        loudnorm = 'loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=' + loudness['input_i'] + ':measured_LRA=' + loudness['input_lra'] + ':measured_TP=' + loudness['input_tp'] + ':measured_thresh=' + loudness['input_thresh'] + ':offset=' + loudness['target_offset'] + ':linear=true:print_format=summary'
        if mv:
            commands += ['-filter_complex', '[0:a]' + loudnorm + '[a1],[a1][1:a]amix=dropout_transition=0:normalize=false[a2]', '-t', '60', '-map', '0:v', '-map', '[a2]']
        else:
            if 'inf' not in loudness['input_i'] and 'inf' not in loudness['input_tp'] and 'inf' not in loudness['target_offset']:
                commands += ['-af', loudnorm]

    commands.append(fout)

    return commands

if __name__ == "__main__":
    main()
