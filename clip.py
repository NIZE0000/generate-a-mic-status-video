import numpy as np
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, VideoFileClip,CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx.all import speedx
from tqdm import tqdm
import os

class Clip:
    def __init__(self, clip_path, min_loud_part_duration, silence_part_speed,
                 default_img, active_img, width, height):
        self.clip = VideoFileClip(clip_path)
        image = Image.open(default_img)
        img_w, img_h = image.size
        self.img = {
            "default": default_img,
            "active": active_img,
            "width": width if width != None else img_w,
            "height": height if width != None else img_h
        }
        Image.new('RGB', (self.img["width"], self.img["height"]), color=(0, 0, 0)).save('BG.png')
        self.clip = (ImageClip('BG.png').set_duration(self.clip.duration)
                     .set_audio(AudioFileClip(clip_path))
                     .set_fps(VideoFileClip(clip_path).fps))
        os.remove('BG.png')
        self.default_clip = (ImageClip(self.img["default"])
                             .set_position(("center", "center"))
                             .resize(width=self.img["width"], height=self.img["height"])
                             )
        self.audio = Audio(self.clip.audio)
        self.active_clip = (ImageClip(self.img["active"])
                            .resize(width=self.img["width"], height=self.img["height"])
                            .set_position(("center", "center")))

        self.min_loud_part_duration = min_loud_part_duration
        self.silence_part_speed = silence_part_speed

    def get_duration(self):
        return self.clip.duration

    def jumpcut(
            self,
            magnitude_threshold_ratio,
            duration_threshold_in_seconds,
            failure_tolerance_ratio,
            space_on_edges,
    ):

        intervals_to_cut = self.audio.get_intervals_to_cut(
            magnitude_threshold_ratio,
            duration_threshold_in_seconds,
            failure_tolerance_ratio,
            space_on_edges,
        )
        jumpcutted_clips = self.jumpcut_silent_parts(intervals_to_cut)
        outputs = concatenate_videoclips(jumpcutted_clips)
        return outputs

    def jumpcut_silent_parts(self, intervals_to_cut):
        jumpcutted_clips = []
        previous_stop = 0
        for start, stop in tqdm(intervals_to_cut, desc="Cutting silent intervals"):
            clip_before = (self.clip.subclip(previous_stop, start))
            clip_before = (CompositeVideoClip([clip_before,
                                               (self.active_clip.set_duration(clip_before.duration))]))

            if clip_before.duration > self.min_loud_part_duration:
                jumpcutted_clips.append(clip_before)

            if self.silence_part_speed is not None:
                silence_clip = self.clip.subclip(start, stop)
                silence_clip = CompositeVideoClip([silence_clip, self.default_clip.set_duration(silence_clip.duration)])
                silence_clip = speedx(
                    silence_clip, self.silence_part_speed
                ).without_audio()
                jumpcutted_clips.append(silence_clip)

            previous_stop = stop

        last_clip = self.clip.subclip(stop, self.clip.duration)
        last_clip = (CompositeVideoClip([last_clip, self.active_clip.set_duration(last_clip.duration)]))
        jumpcutted_clips.append(last_clip)
        return jumpcutted_clips


class Audio:
    def __init__(self, audio):
        self.audio = audio
        self.fps = audio.fps

        self.signal = self.audio.to_soundarray()
        if len(self.signal.shape) == 1:
            self.signal = self.signal.reshape(-1, 1)

    def get_intervals_to_cut(
        self,
        magnitude_threshold_ratio,
        duration_threshold_in_seconds,
        failure_tolerance_ratio,
        space_on_edges,
    ):
        min_magnitude = min(abs(np.min(self.signal)), np.max(self.signal))
        magnitude_threshold = min_magnitude * magnitude_threshold_ratio
        failure_tolerance = self.fps * failure_tolerance_ratio
        duration_threshold = self.fps * duration_threshold_in_seconds
        silence_counter = 0
        failure_counter = 0

        intervals_to_cut = []
        absolute_signal = np.absolute(self.signal)
        for i, values in tqdm(
            enumerate(absolute_signal),
            desc="Getting silent intervals to cut",
            total=len(absolute_signal),
        ):
            silence = all([value < magnitude_threshold for value in values])
            silence_counter += silence
            failure_counter += not silence
            if failure_counter >= failure_tolerance:
                if silence_counter >= duration_threshold:
                    interval_end = (i - failure_counter) / self.fps
                    interval_start = interval_end - (silence_counter / self.fps)

                    interval_start += space_on_edges
                    interval_end -= space_on_edges

                    intervals_to_cut.append(
                        (abs(interval_start), interval_end)
                    )  # in seconds
                silence_counter = 0
                failure_counter = 0
        return intervals_to_cut