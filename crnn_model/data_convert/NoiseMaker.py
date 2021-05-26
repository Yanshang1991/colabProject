import os
import wave
import numpy as np
import random
import time
import utils.file_utils as fu


class NoiseMaker:
    """
    为wav文件增加噪声
    """

    def __init__(self, noise_dir = r""):
        """
        构造方法
        :param noise_dir: 噪声的wav文件所载的目录。会遍历目录、子目录下的所有wav文件
        """
        self.noise_dir = noise_dir
        self.noise_data_cache_map = {}  # 噪音文件缓存
        self.noise_file_path_list = []  # 噪音文件路径
        self.audio_ext = ".wav"  # 音频文件扩展名

        self._get_noise_file_path_list()

    def _get_noise_file_path_list(self):
        """
        读取噪声目录下的wav文件，并存入noise_file_path_list中
        """

        def when_find_ext(path, root, name, ext):
            self.noise_file_path_list.append(path)

        fu.walk_dir(self.noise_dir, self.audio_ext, callback = when_find_ext)

    def _get_random_noise(self):
        """
        从noise_dir中随机获取一个噪声文件
        :return: 噪声数据
        """
        index = random.randint(0, len(self.noise_file_path_list) - 1)
        path = self.noise_file_path_list[index]

        # 先从缓存中查找
        if path in self.noise_data_cache_map.keys():
            return self.noise_data_cache_map[path]

        # 缓存中没有，从磁盘读取该文件
        with wave.open(path, "rb") as wf:
            params = wf.getparams()
            """
            笔记:
                getparams：一次性返回所有的WAV文件的格式信息，它返回的是一个组元(tuple)：
                声道数,      量化位数（byte单位）, 采样频率,  采样点数,  压缩类型,  压缩类型的描述。
                nchannels   sampwidth          framerate  nframes  comptype   compname
                wave模块只支持非压缩的数据，因此可以忽略最后两个信息：
            """
            nchannels, sampwidth, framerate, nframes, comptype, compname = params[:6]
            wr_str_data = wf.readframes(nframes)
            wr_wave_data = np.fromstring(wr_str_data, dtype = np.int16)
            # 降低噪声音量
            # https://blog.csdn.net/u013733326/article/details/78228449
            change_dwmax = wr_wave_data.max() / 100 * 1
            change_dwmin = wr_wave_data.max() / 100 * 0.3

            def waveChange(x, dwmax, dwmin):
                if x != 0:
                    if abs(x) < dwmax and abs(x) > dwmin:
                        x *= 0.2
                    else:
                        x *= 0.1
                return x

            wave_change = np.frompyfunc(waveChange, 3, 1)
            out_wave_data = wave_change(wr_wave_data, change_dwmax, change_dwmin)
            wr_wave_data = out_wave_data.astype(wr_wave_data.dtype)
            self.noise_data_cache_map[path] = (nframes, wr_wave_data)
            return nframes, wr_wave_data

    def deal_file(self, clear_path, out_dir, export = False):
        """
        为单个音频文件添加噪声
        :param clear_path:音频文件路径
        :param out_dir: 添加完噪声的wav文件所在目录
        :param export: 是否返回添加噪声的音频文件。True，返回；False，不返回
        :return: 如果export为True，返回添加噪声的音频文件
        """
        # 随机获取一个音频文件信息
        noise_frames, noise_wave_data = self._get_random_noise()

        # 获取要添加噪音的音频文件的信息
        with wave.open(clear_path, 'rb') as cwf:
            cwf_params = cwf.getparams()
            nchannels, sampwidth, framerate, clear_frames, comptype, compname = cwf_params[:6]
            clear_str_data = cwf.readframes(clear_frames)

        clear_wave_data = np.fromstring(clear_str_data, dtype = np.int16)

        if clear_frames < noise_frames:
            # 噪声截取
            rf1_wave_data = clear_wave_data
            frame_start = random.randint(0, noise_frames - clear_frames)
            rf2_wave_data = noise_wave_data[frame_start:frame_start + clear_frames]
        elif clear_frames > noise_frames:
            # 对不同长度的音频用数据零对齐补位,噪声随机出现在任意位置
            length = abs(noise_frames - clear_frames)
            divide = random.randint(0, length - 1)
            left_array = np.zeros(divide, dtype = np.int16)
            right_array = np.zeros(length - divide, dtype = np.int16)
            rf2_wave_data = np.concatenate((left_array, noise_wave_data, right_array))
            rf1_wave_data = clear_wave_data
        else:
            rf1_wave_data = clear_wave_data
            rf2_wave_data = noise_wave_data

        # ------------------------------    合并源文件和噪声文件的数据    ------------------------------

        new_wave_data = rf1_wave_data + rf2_wave_data

        # 将混合后音频保存到本地
        new_wave = new_wave_data.tostring()

        with wave.open(os.path.join(out_dir, os.path.basename(clear_path)), 'wb') as nwf:
            nwf.setnchannels(nchannels)
            nwf.setsampwidth(sampwidth)
            nwf.setframerate(framerate)
            nwf.writeframes(new_wave)

        # ------------------------------    是否需要返回音频数据    ------------------------------

        if export:
            # 返回处理后音频
            return framerate, new_wave_data

    def deal_dir(self, clear_dir, out_dir):
        """
        给指定目录下的wav文件，添加噪音
        :param clear_dir:要添加噪声的wav所见所载的目录。会遍历目录、子目录下的所有wav文件
        :param out_dir: 添加完噪声的wav文件
        :return:
        """
        assert os.path.exists(clear_dir)
        fu.exists_or_create(out_dir)

        # 遍历目标文件
        def when_find(path, root, name, ext):
            self.deal_file(path, out_dir)

        fu.walk_dir(clear_dir, self.audio_ext, when_find)
