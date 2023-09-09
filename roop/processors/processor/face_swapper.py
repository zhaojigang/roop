import cv2
import insightface
import threading

from roop.processors.processor.face_analyser import get_one_face
from roop.common.helper import resolve_relative_path
from roop.processors.concurrent import multi_process_frame_wrapper

FACE_SWAPPER = None
THREAD_LOCK = threading.Lock()


# 获取换脸模型
def get_face_swapper():
    global FACE_SWAPPER

    with THREAD_LOCK:
        if FACE_SWAPPER is None:
            model_path = resolve_relative_path('../../models/inswapper_128.onnx')
            FACE_SWAPPER = insightface.model_zoo.get_model(model_path, providers='CUDAExecutionProvider')
    return FACE_SWAPPER


def clear_face_swapper():
    global FACE_SWAPPER

    FACE_SWAPPER = None


def post_process():
    clear_face_swapper()


def process_frame(source_face, target_face, temp_frame):
    return get_face_swapper().get(temp_frame, target_face, source_face, paste_back=True)


def process_image(source_path, target_path, output_path):
    # 从 origin_file 中识别脸部
    source_face = get_one_face(cv2.imread(source_path))
    target_frame = cv2.imread(target_path)
    # 从 target_file 中识别脸部
    reference_face = get_one_face(target_frame)
    # 换脸
    result = process_frame(source_face, reference_face, target_frame)
    # 将换脸结果写入 output_file
    cv2.imwrite(output_path, result)


def process_video(source_path, temp_frame_paths):
    multi_process_frame_wrapper(source_path, temp_frame_paths, process_frames)


def process_frames(source_path, temp_frame_paths, update_tqdm):
    source_face = get_one_face(cv2.imread(source_path))
    for temp_frame_path in temp_frame_paths:
        temp_frame = cv2.imread(temp_frame_path)
        result = process_frame(source_face, get_one_face(temp_frame), temp_frame)
        cv2.imwrite(temp_frame_path, result)
        if update_tqdm:
            update_tqdm()
