#!/usr/bin/env python3

import sys
import shutil
import warnings
from roop.common.predictor import predict_image, predict_video
from roop.processors.processor.face_swapper import process_image, process_video
from roop.processors.processor.face_enhancer import process_image as gfpgan_enhance_image
from roop.common.helper import is_image, is_video, detect_fps, create_video, extract_frames, \
    get_temp_frame_paths, restore_audio, create_temp, clean_temp
from roop.common.biz_exception import BizException

warnings.filterwarnings('ignore', category=FutureWarning, module='insightface')
warnings.filterwarnings('ignore', category=UserWarning, module='torchvision')

def swap(source_file, target_file, output_file):
    if is_image(target_file):
        handle_image_swap(source_file, target_file, output_file)
    if is_video(target_file):
        handle_video_swap(source_file, target_file, output_file)


def handle_image_swap(source_file, target_file, output_file):
    if predict_image(target_file):
        raise BizException(400, '按照法律法规要求，请上传合规的文件')
    shutil.copy2(target_file, output_file)
    # process processor
    process_image(source_file, output_file, output_file)
    gfpgan_enhance_image(source_file, output_file, output_file)
    # frame_processor.post_process()


def handle_video_swap(source_file, target_file, output_file):
    if predict_video(target_file):
        raise BizException(400, '按照法律法规要求，请上传合规的文件')
    create_temp(target_file)
    # extract frames
    fps = detect_fps(target_file)
    extract_frames(target_file, fps)
    # process processor
    temp_frame_paths = get_temp_frame_paths(target_file)
    process_video(source_file, temp_frame_paths)
    # frame_processor.post_process()
    # create video
    create_video(target_file, fps)
    # handle audio
    restore_audio(target_file, output_file)
    # clean temp
    clean_temp(target_file)


def destroy():
    sys.exit()
