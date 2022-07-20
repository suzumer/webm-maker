import re
import subprocess
import argparse
import os
from tempfile import TemporaryDirectory
from pathlib import Path

CONVERT = 1024*1024*8

parser = argparse.ArgumentParser(usage="WebM Maker", description="A program to create webms for 4chan")
parser.add_argument('--scale', help='How to scale the video',default='None')
parser.add_argument('--fps', help='Video framerate',default='None')
parser.add_argument('--audio', help='Audo quality 0-10',default='3')
parser.add_argument('--no-audio', help='No audio',action='store_true')
parser.add_argument('-i', help="Name of input video",default='None')
parser.add_argument('--size',help="Size of output file in megabytes",default=6.0,type=float)
parser.add_argument('output', help="Name of output video")
args = parser.parse_args()

def get_length(path):
    run = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',str(path)],capture_output=True)
    length = float(run.stdout.decode('UTF-8').strip())
    return length

#size in bits
def get_size(path):
    file_size = os.path.getsize(str(path))*8
    return file_size
vpxpath = Path("D:\\Code\\webm-maker\\vpxenc.exe")
tempdir = TemporaryDirectory()
tempdirpath = Path(tempdir.name)
inputpath = Path(args.i)
outputpath = Path(args.output)
vorbispath = tempdirpath / 'audio.webm'
y4mpath = tempdirpath / 'video.y4m'
vp8path = tempdirpath / 'video.webm'
length = get_length(inputpath)
vorbissize = 0
subprocess.run(['ffmpeg','-i',str(inputpath)] +
    (['-an','-sws_flags','lanczos', '-vf',f'scale={args.scale}'] if args.scale != 'None' else []) +
    (['-r',args.fps] if args.fps != 'None' else []) +
    [str(y4mpath)])
if not args.no_audio:
    subprocess.run(['ffmpeg','-i',str(inputpath),'-vn','-q:a', args.audio,'-ac','2','-c:a','libvorbis', str(vorbispath)])
    vorbissize = get_size(vorbispath)

targetbitrate = int((args.size*CONVERT - vorbissize)/(1024*length))
subprocess.run([str(vpxpath),'--codec=vp8', f'--target-bitrate={targetbitrate}', '--best', '--end-usage=vbr', '--auto-alt-ref=1', '--passes=2', '--threads=7', '-o', str(vp8path), str(y4mpath)])
if args.no_audio:
    subprocess.run(['ffmpeg','-y','-i',str(vp8path),'-c:v','copy', '-map', '0:v:0','-an', str(outputpath)])
else:
    subprocess.run(['ffmpeg','-y','-i',str(vp8path),'-i',str(vorbispath),'-c:v','copy','-c:a','copy', '-map', '0:v:0','-map','1:a:0', str(outputpath)])

tempdir.cleanup()

