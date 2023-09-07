import cv2
import threading
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

from roop.common.helper import resolve_relative_path

FRAME_PROCESSOR = None
THREAD_SEMAPHORE = threading.Semaphore()
THREAD_LOCK = threading.Lock()


def get_real_esrgan_processor():
	global FRAME_PROCESSOR

	with THREAD_LOCK:
		if FRAME_PROCESSOR is None:
			model_path = resolve_relative_path('../../models/RealESRGAN_x4plus.pth')
			FRAME_PROCESSOR = RealESRGANer(
				model_path = model_path,
				model = RRDBNet(
					num_in_ch = 3,
					num_out_ch = 3,
					num_feat = 64,
					num_block = 23,
					num_grow_ch = 32,
					scale = 4
				),
				device = 'cuda',
				tile = 512,
				tile_pad = 32,
				pre_pad = 0,
				scale = 4
			)
	return FRAME_PROCESSOR


def clear_frame_processor():
	global FRAME_PROCESSOR

	FRAME_PROCESSOR = None


def post_process():
	clear_frame_processor()


def enhance_frame(temp_frame):
	with THREAD_SEMAPHORE:
		temp_frame, _ = get_real_esrgan_processor().enhance(temp_frame, outscale = 1)
	return temp_frame


def process_frame(source_face, reference_face, temp_frame):
	return enhance_frame(temp_frame)


def process_frames(source_path, temp_frame_paths):
	for temp_frame_path in temp_frame_paths:
		temp_frame = cv2.imread(temp_frame_path)
		result_frame = process_frame(None, None, temp_frame)
		cv2.imwrite(temp_frame_path, result_frame)


def process_image(source_path, target_path, output_path):
	target_frame = cv2.imread(target_path)
	result = process_frame(None, None, target_frame)
	cv2.imwrite(output_path, result)


def process_video(source_path, temp_frame_paths):
	process_frames(source_path, temp_frame_paths)
