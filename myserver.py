from flask import Flask, request, jsonify

import roop.globals
from roop.processors.frame.core import pre_load_processor_modules
from roop.core import swap_face_with_image_for_web
from roop.common.biz_exception import BizException

app = Flask(__name__)


# 换脸
@app.route('/swap_face_with_image', methods=['POST', 'GET'])
def swap_face_with_image():
    data = request.get_json()
    mode = data.get("mode")
    face_img_path = data.get("faceImagePath")
    target_path = data.get("targetImagePath")
    output_path = data.get("outputImagePath")
    swap_face_with_image_for_web(mode, face_img_path, target_path, output_path)
    return jsonify({
        "code": 200,
        "message": "success",
        "data": target_path
    })


# 全局异常处理器
@app.errorhandler(Exception)
def error_handler(e):
    if isinstance(e, BizException):
        return jsonify({
            "code": e.code,
            "message": e.message,
            "data": None
        })
    else:
        return jsonify({
            "code": 500,
            "message": "换脸失败，请稍后重试",
            "data": None
        })


if __name__ == '__main__':
    # cpu:CPUExecutionProvider  gpu:CUDAExecutionProvider
    roop.globals.execution_providers = ['CUDAExecutionProvider']
    roop.globals.similar_face_distance = 1.5
    roop.globals.reference_face_position = 0
    # 预加载模型
    pre_load_processor_modules()
    app.run()
