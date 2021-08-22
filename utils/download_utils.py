import os
import requests
import time
import threading
from urllib.parse import urlparse

max_thread_size = 10  # 最大线程数量


class DownloadThread(threading.Thread):
	def __init__(self, name, url, tar_dir):
		threading.Thread.__init__(self)
		self.name = name
		self.url = url
		self.tar_dir = tar_dir

	def run(self):
		print("开启线程：" + self.name)
		single(self.url, self.tar_dir, self.name)
		print("退出线程：" + self.name)


def many(urls, tar_dir = "/content/drive/MyDrive/Download/", mul_thread = False):
	"""
	同时下载多个文件
	"""
	if mul_thread:  # 多线程下载
		thread_size = 0
		threads = []
		for url in urls:
			thread_size += 1
			thread = DownloadThread(name = ("Thread_" + str(thread_size)), url = url, tar_dir = tar_dir)
			thread.start()
			threads.append(thread)
		for thread in threads:
			thread.join()
	else:
		for url in urls:
			single(url, tar_dir)
	print("下载结束")


def single(url, tar_dir, name):

	start = time.time()  # 记录开始时间
	response = requests.get(url, stream = True)  # 读取文件
	size = 0  # 初始化已下载大小
	chunk_size = 10200  # 下载内容的大小，10M
	content_size = int(response.headers['content-length'])  # 下载文件总大小

	if response.status_code == 200:  # 请求成功
		print("Start download, [File size]:{size:.2f} MB".format(size = content_size / chunk_size / 1024))
		filepath = os.path.join(tar_dir, name)  # 文件的存储路径
		with open(filepath, "wb") as file:
			for data in response.iter_content(chunk_size = chunk_size):
				file.write(data)
				size += len(data)
				print('\r' + '%s [下载进度]:%s%.2f%%' % (name, '>' * int(size * 50 / content_size), float(size / content_size * 100)), end = ' ')
		end = time.time()  # 下载结束时间
		print('Download completed!,times: %.2f秒' % (end - start))  # 输出下载用时时间
