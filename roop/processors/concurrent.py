import os
import psutil
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def multi_process_frame_wrapper(source_path, temp_frame_paths, process_frames):
    progress_bar_format = '{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'
    with tqdm(total=len(temp_frame_paths), desc='Processing', unit='frame', dynamic_ncols=True,
              bar_format=progress_bar_format) as progress:
        multi_process_frame(source_path, temp_frame_paths, process_frames, lambda: update_progress(progress))


def update_progress(progress):
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024 / 1024
    progress.set_postfix({
        # 'memory_usage': '{:.2f}'.format(memory_usage).zfill(5) + 'GB',
        'execution_threads': 8
    })
    progress.refresh()
    progress.update(1)


def multi_process_frame(source_path, temp_frame_paths, process_frames, update_p):
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        # 将全部帧推入队列
        queue = create_queue(temp_frame_paths)
        # 每个线程一次处理多少个帧
        frames_per_future = max(len(temp_frame_paths) // 8, 1)
        # 队列不为空，则将所有帧分配给每个线程（每个线程分配到N个帧，每个线程内部进行多帧串行处理）
        while not queue.empty():
            future = executor.submit(process_frames, source_path, pick_queue(queue, frames_per_future), update_p)
            futures.append(future)
        # 等待所有帧结束
        for future in as_completed(futures):
            future.result()


# 将所有帧推入队列
def create_queue(temp_frame_paths):
    queue: Queue[str] = Queue()
    for frame_path in temp_frame_paths:
        queue.put(frame_path)
    return queue


# 从队列中取出 frames_per_future 个帧
def pick_queue(queue, frames_per_future):
    queues = []
    for _ in range(frames_per_future):
        if not queue.empty():
            queues.append(queue.get())
    return queues
