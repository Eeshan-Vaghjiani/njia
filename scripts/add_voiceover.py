"""Add an authorised voice recording to the existing 90-second demo.

Usage: python scripts/add_voiceover.py --audio "path/to/recording.m4a"
Requires ffmpeg/ffprobe on PATH. Original audio stays outside the repository.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio', required=True)
    args = parser.parse_args()
    audio = Path(args.audio)
    ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        raise SystemExit('ffmpeg and ffprobe must be on PATH')
    target = ROOT / 'artifacts/njia-demo-90s.mp4'
    backup = target.with_name('njia-demo-90s-silent.mp4')
    temporary = target.with_name('njia-demo-90s-narrated.mp4')
    def probe(path):
        return json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))
    source_info, audio_info = probe(target), probe(audio)
    duration = float(source_info['format']['duration'])
    audio_duration = float(audio_info['format']['duration'])
    if abs(duration - 90) > .05 or audio_duration > 90:
        raise SystemExit('Expected a 90-second video and a voice recording no longer than 90 seconds')
    if not backup.exists():
        shutil.copy2(target, backup)
    subprocess.run([ffmpeg, '-hide_banner', '-y', '-i', str(target), '-i', str(audio),
                    '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
                    '-af', 'highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=duration=90',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                    '-t', '90', '-movflags', '+faststart', str(temporary)], check=True)
    result = probe(temporary)
    assert abs(float(result['format']['duration']) - 90) < .05
    assert any(s['codec_type'] == 'audio' and s['codec_name'] == 'aac' for s in result['streams'])
    def video_hash(path):
        return subprocess.check_output([ffmpeg, '-v', 'error', '-i', str(path), '-map', '0:v:0', '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).decode().strip()
    assert video_hash(target) == video_hash(temporary), 'Video stream must remain unchanged'
    os.replace(temporary, target)
    report = {'duration_seconds':90, 'input_voice_seconds':audio_duration, 'audio':'user-provided human narration',
              'codec':'AAC', 'video_stream_unchanged':True, 'voice_speed':1.0,
              'alignment':'Starts at 0 seconds; original pauses retained; silence padded to 90 seconds',
              'processing':'70 Hz high-pass and loudness normalization, AAC 192 kbps',
              'bytes':target.stat().st_size, 'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
              'public_url':'https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.mp4'}
    (ROOT / 'artifacts/narration-results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
