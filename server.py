from flask import Flask, request, jsonify

from roop.core import swap
from roop.common.biz_exception import BizException

app = Flask(__name__)


@app.route('/swap_face', methods=['POST', 'GET'])
def swap_face():
    data = request.get_json()
    origin_file = data.get("originFile")
    target_file = data.get("targetFile")
    output_file = data.get("outputFile")
    swap(origin_file, target_file, output_file)
    return jsonify({
        "code": 200,
        "message": "success"
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
    app.run()
