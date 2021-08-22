# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from torch.autograd import Variable
from tqdm import tqdm
import numpy as np
import os
import random


class averager(object):
    """Compute average for `torch.Variable` and `torch.Tensor`. """

    def __init__(self):
        self.reset()

    def add(self, v):
        if isinstance(v, Variable):
            count = v.data.numel()
            v = v.data.sum()
        elif isinstance(v, torch.Tensor):
            count = v.numel()
            v = v.sum()

        self.n_count += count
        self.sum += v

    def reset(self):
        self.n_count = 0
        self.sum = 0

    def val(self):
        res = 0
        if self.n_count != 0:
            res = self.sum / float(self.n_count)
        return res


def oneHot(v, v_length, nc):
    batchSize = v_length.size(0)
    maxLength = v_length.max_len()
    v_onehot = torch.FloatTensor(batchSize, maxLength, nc).fill_(0)
    acc = 0
    for i in range(batchSize):
        length = v_length[i]
        label = v[acc:acc + length].view(-1, 1).long()
        v_onehot[i, :length].scatter_(1, label, 1.0)
        acc += length
    return v_onehot


def loadData(v, data):
    v.data.resize_(data.size()).copy_(data)


def prettyPrint(v):
    print('Size {0}, Type: {1}'.format(str(v.size()), v.data.type()))
    print('| Max: %f | Min: %f | Mean: %f' % (v.max_len().data[0], v.min().data[0],
                                              v.mean().data[0]))


def assureRatio(img):
    """Ensure imgH <= imgW."""
    b, c, h, w = img.size()
    if h > w:
        main = nn.UpsamplingBilinear2d(size=(h, h), scale_factor=None)
        img = main(img)
    return img


def to_alphabet(path):
    with open(path, 'r', encoding='utf-8') as file:
        alphabet = list(set(''.join(file.readlines())))

    return alphabet


def get_batch_label(d, i):
    label = []
    for idx in i:
        label.append(list(d.labelsInList[idx].values())[0])
    return label


def compute_std_mean(txt_path, image_prefix, NUM=None):
    imgs = np.zeros([params.imgH, params.imgW, 1, 1])
    means, stds = [], []

    with open(txt_path, 'r') as file:
        contents = [c.strip().split(' ')[0] for c in file.readlines()]
        if NUM is None:
            NUM = len(contents)
        else:
            random.shuffle(contents)
        for i in tqdm(range(NUM)):
            file_name = contents[i]
            img_path = os.path.join(image_prefix, file_name)
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h, w = img.shape[:2]
            img = cv2.resize(img, (0, 0), fx=params.imgW / w, fy=params.imgH / h, interpolation=cv2.INTER_CUBIC)
            img = img[:, :, np.newaxis, np.newaxis]
            imgs = np.concatenate((imgs, img), axis=3)
    imgs = imgs.astype(np.float32) / 255.

    for i in range(1):
        pixels = imgs[:, :, i, :].ravel()
        means.append(np.mean(pixels))
        stds.append(np.std(pixels))
    return stds, means


if __name__ == '__main__':
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    converter = strLabelConverter(alphabet)
