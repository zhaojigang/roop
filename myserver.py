from flask import Flask,request

import roop.globals
from roop.processors.frame.core import pre_load_processor_modules
from roop.core import swap_face_with_image_for_web

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    return 'home'


@app.route('/swap_face_with_image', methods=['POST', 'GET'])
def swap_face_with_image():
    data = request.get_json()
    mode = data.get("mode")
    face_img_path = data.get("faceImagePath")
    target_path = data.get("targetImagePath")
    output_path = data.get("outputImagePath")
    return swap_face_with_image_for_web(mode, face_img_path, target_path, output_path)


if __name__ == '__main__':
    # cpu:CPUExecutionProvider  gpu:CUDAExecutionProvider
    roop.globals.execution_providers = ['CPUExecutionProvider']
    roop.globals.similar_face_distance = 1.5
    roop.globals.reference_face_position = 0
    # 预加载模型
    pre_load_processor_modules()
    app.run()
