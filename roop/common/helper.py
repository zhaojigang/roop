import glob
import mimetypes
import os
import shutil
import subprocess
from pathlib import Path

TEMP_DIRECTORY = 'temp'
TEMP_VIDEO_FILE = 'temp.mp4'


def run_ffmpeg(args):
    commands = ['ffmpeg', '-hide_banner']
    commands.extend(args)
    try:
        subprocess.check_output(commands, stderr=subprocess.STDOUT)
        return True
    except Exception:
        pass
    return False


def detect_fps(target_path):
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of',
               'default=noprint_wrappers=1:nokey=1', target_path]
    output = subprocess.check_output(command).decode().strip().split('/')
    try:
        numerator, denominator = map(int, output)
        return numerator / denominator
    except Exception:
        pass
    return 30


# 抽帧到临时文件夹
def extract_frames(target_path, fps=30):
    temp_directory_path = get_temp_directory_path(target_path)
    temp_frame_quality = 0 * 31 // 100
    return run_ffmpeg(
        ['-hwaccel', 'auto', '-i', target_path, '-q:v', str(temp_frame_quality), '-pix_fmt', 'rgb24', '-vf',
         'fps=' + str(fps), os.path.join(temp_directory_path, '%04d.png')])


# 创建视频
def create_video(target_path, fps=30):
    temp_output_path = get_temp_output_path(target_path)
    temp_directory_path = get_temp_directory_path(target_path)
    output_video_quality = (35 + 1) * 51 // 100
    commands = ['-hwaccel', 'auto', '-r', str(fps), '-i',
                os.path.join(temp_directory_path, '%04d.png'), '-c:v',
                'libx264',
                '-crf', str(output_video_quality),
                '-pix_fmt', 'yuv420p', '-vf', 'colorspace=bt709:iall=bt601-6-625:fast=1', '-y', temp_output_path]
    return run_ffmpeg(commands)


# 补充音频
def restore_audio(target_path, output_path):
    temp_output_path = get_temp_output_path(target_path)
    done = run_ffmpeg(
        ['-hwaccel', 'auto', '-i', temp_output_path, '-i', target_path, '-c:v', 'copy', '-map', '0:v:0', '-map',
         '1:a:0', '-y', output_path])
    if not done:
        # 将无音频的视频移动到output_file，进行返回
        move_temp(target_path, output_path)


def get_temp_frame_paths(target_path):
    temp_directory_path = get_temp_directory_path(target_path)
    return glob.glob((os.path.join(glob.escape(temp_directory_path), '*.png')))


# 视频换脸：创建临时文件夹，存储临时帧/临时视频文件
def create_temp(target_path):
    temp_directory_path = get_temp_directory_path(target_path)
    Path(temp_directory_path).mkdir(parents=True, exist_ok=True)


# 视频换脸：临时文件夹 target_path.split('.')[0]+'TEMP'+target_path.split('.')[1]
def get_temp_directory_path(target_path):
    target_name, _ = os.path.splitext(os.path.basename(target_path))
    target_directory_path = os.path.dirname(target_path)
    return os.path.join(target_directory_path, TEMP_DIRECTORY, target_name)


# 视频换脸：获取临时视频文件路径
def get_temp_output_path(target_path):
    temp_directory_path = get_temp_directory_path(target_path)
    return os.path.join(temp_directory_path, TEMP_VIDEO_FILE)


def move_temp(target_path, output_path):
    temp_output_path = get_temp_output_path(target_path)
    if os.path.isfile(temp_output_path):
        if os.path.isfile(output_path):
            os.remove(output_path)
        shutil.move(temp_output_path, output_path)


# 清理 temp 文件夹
def clean_temp(target_path: str) -> None:
    temp_directory_path = get_temp_directory_path(target_path)
    parent_directory_path = os.path.dirname(temp_directory_path)
    if os.path.isdir(temp_directory_path):
        shutil.rmtree(temp_directory_path)
    if os.path.exists(parent_directory_path) and not os.listdir(parent_directory_path):
        os.rmdir(parent_directory_path)


def is_image(image_path: str) -> bool:
    if image_path and os.path.isfile(image_path):
        mimetype, _ = mimetypes.guess_type(image_path)
        return bool(mimetype and mimetype.startswith('image/'))
    return False


def is_video(video_path: str) -> bool:
    if video_path and os.path.isfile(video_path):
        mimetype, _ = mimetypes.guess_type(video_path)
        return bool(mimetype and mimetype.startswith('video/'))
    return False


def resolve_relative_path(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))
