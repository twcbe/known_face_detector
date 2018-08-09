import time

class Fps():
    def __init__(self, average_over_frames=50):
        self.average_over_frames = average_over_frames

    def start(self):
        self.global_start_time = time.time()
        self.frame_times = [self.global_start_time]
        self.frame = 0

    def update(self):
        self.frame = self.frame + 1
        self.frame_times.append(time.time())
        self.frame_times = self.frame_times[-self.average_over_frames:]

    def elapsed(self):
        return self.frame_times[-1] - self.global_start_time

    def fps(self):
        return (len(self.frame_times) - 1.0) / (self.frame_times[-1] - self.frame_times[0])

    def info(self):
        return "frame: %5d  fps: %3.2f last_frame: %1.3f sec  elapsed: %3.2f sec" % (self.frame, self.fps(), (self.frame_times[-1] - self.frame_times[-2]), self.elapsed())
