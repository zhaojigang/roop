import threading
import insightface
from roop.common.biz_exception import BizException
from roop.common.helper import resolve_relative_path

FACE_ANALYSER = None
THREAD_LOCK = threading.Lock()


# 获取人脸分析器（识别人脸）
def get_face_analyser():
    global FACE_ANALYSER

    with THREAD_LOCK:
        if FACE_ANALYSER is None:
            root = resolve_relative_path('../../models')
            # cpu:CPUExecutionProvider  gpu:CUDAExecutionProvider
            FACE_ANALYSER = insightface.app.FaceAnalysis(name='buffalo_l', root=root, providers='CUDAExecutionProvider')
            FACE_ANALYSER.prepare(ctx_id=0)
    return FACE_ANALYSER


def get_one_face(frame):
    return get_many_faces(frame)[0]


def get_many_faces(frame):
    try:
        return get_face_analyser().get(frame)
    except ValueError:
        raise BizException(400, '当前图片未检测到脸部，请重新上传图片')
