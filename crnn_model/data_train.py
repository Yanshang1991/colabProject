# -*- coding: utf-8 -*-
"""
"""

import argparse
import os

import random
import torch.backends.cudnn as cudnn
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
# from torch.autograd import Variable
import numpy as np
from torch.nn import CTCLoss

import data_convert
import data_loss
import data_model as crnn_model
from data_read import GetDataset
import Levenshtein
from torch.utils.tensorboard import SummaryWriter
import matplotlib.pyplot as plt


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        m.weight.data.normal_(0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        m.weight.data.normal_(1.0, 0.02)
        m.bias.data.fill_(0)


def train(crnn, train_loader, criterion, epoch):
    for p in crnn.parameters():
        p.requires_grad = True

    # set the calculation of loss
    loss_avg = data_loss.averager()

    for i_batch, (image, index, phonemeText) in enumerate(train_loader):

        if True:
            for index, img in enumerate(image):
                # imgName = '/home/tk_nd/workfile/crnn_model/tmp/' + str(index) + '.png'
                # print(imgName)
                a = img.numpy().squeeze()
                imgName = str(index) + '.png'
                # a=img.cpu().numpy().squeeze()
                # print(a.shape)
                # print(type(a))
                # print(img.cpu().numpy())
                # fig, ax = plt.subplots()
                # ax.imshow(a, origin = 'lower',cmap='Greys')
                plt.imshow(a, origin = 'lower', cmap = 'Greys')
                plt.axis('off')
                # plt.show()
                plt.savefig(imgName, dpi = 300)
                plt.close()

        image = image.to(device)  # 13,1,256,1200
        batch_size = image.size(0)
        preds = crnn(image)  # 301,13,183

        label_text, label_length = converter.encodePhn(phonemeText)

        preds_size = torch.IntTensor([preds.size(0)] * batch_size)

        cost = criterion(preds, label_text, preds_size, label_length) / batch_size
        crnn.zero_grad()

        cost.backward()
        optimizer.step()
        loss_avg.add(cost)

        print('nbatch=%d,loss=%f' % (i_batch, loss_avg.val()))
        loss_avg.reset()

def val(net, dataset, criterion, max_iter = 100):
    # net=crnn
    for p in net.parameters():
        p.requires_grad = False

    net.eval()
    val_iter = iter(val_loader)

    loss_avg = data_loss.averager()

    max_iter = min(max_iter, len(val_loader))
    for i in range(max_iter):
        data = val_iter.next()

        valimage, index, valText = data
        batch_size = valimage.size(0)
        t, l = converter.encodePhn(valText)

        preds = net(valimage)
        preds_size = torch.IntTensor([preds.size(0)] * batch_size)

        cost = criterion(preds, t, preds_size, l) / batch_size
        loss_avg.add(cost)
        loss_avg.reset()

        _, pred_result = preds.max(2)
        # pred_result = pred_result.squeeze(2)
        pred_result = pred_result.transpose(1, 0)
        pred_result = pred_result.contiguous().view(-1)
        sim_preds, addr = converter.decodePhn(pred_result.numpy(), preds_size.data, raw = False)

        sum_corr = 0
        for predValue, orgValue in zip(sim_preds, valText):
            print('========================= compare  character =========================')
            print(orgValue)
            # print('========================= the predict character =========================')
            print(predValue)

            str1 = predValue.replace(' ', '')
            str2 = orgValue.replace(' ', '')
            corr = Levenshtein.ratio(str1, str2)
            sum_corr = sum_corr + corr
        sum_corr = sum_corr / batch_size
        print("the average error of this epoch is %f" % (1 - sum_corr))


if __name__ == '__main__':

    # ---------------     predefined parameters   ---------------
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type = int, help = 'number of data loading workers', default = 4)
    parser.add_argument('--batchSize', type = int, default = 32, help = 'input batch size')
    parser.add_argument('--imgH', type = int, default = 160, help = 'the height of the input image to network')
    parser.add_argument('--imgW', type = int, default = 1200, help = 'the width of the input image to network')

    parser.add_argument('--window_ms', type = int, default = 20, help = 'the duration of hann window millisecond')
    parser.add_argument('--stride_ms', type = int, default = 10, help = 'the duration of a stride millisecond')
    parser.add_argument('--sr', type = int, default = 16000, help = 'default sample rate')

    parser.add_argument('--nh', type = int, default = 512, help = 'size of the lstm hidden state')
    parser.add_argument('--nepoch', type = int, default = 100, help = 'number of epochs to train for')
    parser.add_argument('--train_dir', default = r'/content/dataset', help = 'path of train data')
    parser.add_argument('--val_dir', default = r'/content/dataset', help = 'path of val data')

    parser.add_argument('--wrdtxtfile', default = r'/content/label', help = 'path of val data')
    parser.add_argument('--phntxtfile', default = r'/content/label', help = 'path of val data')
    parser.add_argument('--phoneme_file', default = r'/content/colabProject/crnn_model/dataset/phoneme_label.txt', help = 'path of val data')
    parser.add_argument('--word_file', default = r'/content/colabProject/crnn_model/dataset/wrds_label.txt', help = 'path of val data')

    parser.add_argument('--cuda', action = 'store_true', help = 'enables cuda')
    parser.add_argument('--ngpu', type = int, default = 1, help = 'number of GPUs to use')

    parser.add_argument('--pretrained', default = r'', help = "path to pretrained model (to continue training)")

    parser.add_argument('--pic_path', default = r'/content/colabProject/crnn_model/train_pic/', help = "path to load pics")
    parser.add_argument('--expr_dir', default = r'/content/colabProject/crnn_model/expr/', help = 'Where to store samples and models')
    parser.add_argument('--displayInterval', type = int, default = 10, help = 'Interval to be displayed')
    parser.add_argument('--n_test_disp', type = int, default = 10, help = 'Number of samples to display when test')
    parser.add_argument('--valInterval', type = int, default = 300, help = 'Interval to be displayed')
    parser.add_argument('--saveInterval', type = int, default = 2, help = 'Interval to be displayed')
    parser.add_argument('--lr', type = float, default = 0.0001, help = 'learning rate for Critic, not used by adadealta')
    parser.add_argument('--beta1', type = float, default = 0.5, help = 'beta1 for adam. default=0.5')
    parser.add_argument('--adam', action = 'store_true', help = 'Whether to use adam (default is rmsprop)')
    parser.add_argument('--adadelta', action = 'store_true', help = 'Whether to use adadelta (default is rmsprop)')
    parser.add_argument('--keep_ratio', action = 'store_true', help = 'whether to keep ratio for image resize')
    parser.add_argument('--manualSeed', type = int, default = 10, help = 'reproduce experiemnt')
    parser.add_argument('--random_sample', action = 'store_true', help = 'whether to sample the dataset with random sampler')
    params = parser.parse_args()

    # os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    # 设置tensorBoard
    # default `log_dir` is "runs" - we'll be more specific here

    if not os.path.exists(params.expr_dir):
        os.makedirs(params.expr_dir)
    tensorboard_file = os.path.join(params.expr_dir, 'train_tensorboard')
    writer = SummaryWriter('runs/image_classify_tensorboard')

    random.seed(params.manualSeed)
    np.random.seed(params.manualSeed)
    torch.manual_seed(params.manualSeed)

    # accelerate the calculation
    # cudnn.deterministic = True
    # cudnn.benchmark = True

    # set default device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # ----------------  read phonemes
    if params.phoneme_file != '':
        # GetPhonemes()
        phoneme_list = []
        params.phoneme_file = os.path.join(os.getcwd(), params.phoneme_file)
        with open(params.phoneme_file, 'r', encoding = 'utf-8') as fr:
            for c in fr.readlines():
                c = c.replace("\n", "")
                phoneme_list.append(c)

    # -----------------  read data
    label_path = os.path.join(os.getcwd(), params.phntxtfile)
    trainpath = os.path.join(os.getcwd(), params.train_dir)
    valpath = os.path.join(os.getcwd(), params.val_dir)

    assert os.path.exists(label_path)
    assert os.path.exists(trainpath)
    assert os.path.exists(valpath)

    # -----------------  generate data
    train_dataset = GetDataset(trainpath, label_path, params)
    val_dataset = GetDataset(valpath, label_path, params)

    train_loader = DataLoader(train_dataset, batch_size = params.batchSize, shuffle = True, num_workers = params.workers)
    val_loader = DataLoader(val_dataset, batch_size = params.batchSize, shuffle = True, num_workers = params.workers)

    # ----------------- begin train
    # set the parameters for train

    params.imgH = int(0.001 * params.sr * params.window_ms) // 2

    # # set the loss function
    nc = 1  # cnn core
    criterion = CTCLoss(reduction = 'sum')

    converter = data_convert.strLabelConverter(phoneme_list)

    # set the max classes
    nclass = len(phoneme_list)

    # # cnn and rnn
    crnn = crnn_model.CRNN(params.imgH, nc, nclass, params.nh)
    crnn.apply(weights_init)

    crnn = crnn.to(device)
    criterion = criterion.to(device)

    if params.pretrained != '':
        print('loading pretrained model from %s' % params.pretrained)
        crnn.load_state_dict(torch.load(params.pretrained, map_location = torch.device(device)))  # crnn.load_state_dict(torch.load('crnn_best.pth',map_location=torch.device('cpu')))

    if params.adam:
        optimizer = optim.Adam(crnn.parameters(), lr = params.lr, betas = (params.beta1, 0.999))
    elif params.adadelta:
        optimizer = optim.Adadelta(crnn.parameters(), lr = params.lr)
    else:
        optimizer = optim.RMSprop(crnn.parameters(), lr = params.lr)

    for i_epoch in range(params.nepoch):
        print('========== epoch = %d ==========' % (i_epoch))
        train(crnn, train_loader, criterion, params.nepoch)
        torch.save(crnn.state_dict(), r'/content/drive/MyDrive/t0525.pth')

