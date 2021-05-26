# coding:utf-8
"""
 CRNN Net

"""

import torch.nn as nn
import torch.nn.functional as F


class BidirectionalLSTM(nn.Module):
    # Inputs hidden units Out
    def __init__(self, nIn, nHidden, nOut):
        super(BidirectionalLSTM, self).__init__()  # nn.Module子类的函数必须在构造函数中执行父类的构造函数

        self.rnn = nn.LSTM(nIn, nHidden, bidirectional=True)
        self.embedding = nn.Linear(nHidden * 2, nOut)

    def forward(self, input):
        # print(f"input size: {len(input)}")
        # print(input)
        recurrent, _ = self.rnn(input)
        T, b, h = recurrent.size()
        t_rec = recurrent.view(T * b, h)

        output = self.embedding(t_rec)  # [T * b, nOut]
        output = output.view(T, b, -1)

        return output


class CRNN(nn.Module):
    #                   32    1   37     256
    def __init__(self, imgH, nc, nclass, nh, n_rnn=2, leakyRelu=False):
        super(CRNN, self).__init__()
        assert imgH % 16 == 0, 'imgH has to be a multiple of 16'

        ks = [3, 3, 3, 3, 3, 3, 2]
        ps = [1, 1, 1, 1, 1, 1, 0]
        ss = [1, 1, 1, 1, 1, 1, 1]
        # nm = [64, 128, 256, 256, 512, 512, 512]
        # nm = [32, 64, 128, 128, 256, 256, 256]
        # nm = [8, 32, 64, 64, 128, 128, 128]        
        nm = [8, 32, 64, 64, 64, 64, 64]
        # nm = [8, 16, 32, 32, 64, 64, 64]
        
        # nm = [64, 128, 256, 256, 512, 512, 512]
        
        cnn = nn.Sequential()

        def convRelu(i, batchNormalization=False):
            nIn = nc if i == 0 else nm[i - 1]
            nOut = nm[i]
            cnn.add_module('conv{0}'.format(i),
                           nn.Conv2d(nIn, nOut, ks[i], ss[i], ps[i]))
            if batchNormalization:
                cnn.add_module('batchnorm{0}'.format(i), nn.BatchNorm2d(nOut))
            if leakyRelu:
                cnn.add_module('relu{0}'.format(i),
                               nn.LeakyReLU(0.2, inplace=True))
            else:
                cnn.add_module('relu{0}'.format(i), nn.ReLU(True))

        convRelu(0)
        cnn.add_module('pooling{0}'.format(0), nn.MaxPool2d(2, 2))  # 64x16x64
        convRelu(1)
        cnn.add_module('pooling{0}'.format(1), nn.MaxPool2d(2, 2))  # 128x8x32
        convRelu(2, True)

        # cnn.add_module('pooling{0}'.format(1), nn.MaxPool2d(2, 2))###########
        convRelu(3)
        cnn.add_module('pooling{0}'.format(2),
                       nn.MaxPool2d((2, 2), (2, 1), (0, 1)))  # 256x4x16
        convRelu(4, True)
        # cnn.add_module('pooling{0}'.format(2), nn.MaxPool2d(2, 2))  ###########

        convRelu(5)
        cnn.add_module('pooling{0}'.format(3),
                       nn.MaxPool2d((2, 2), (2, 1), (0, 1)))  # 512x2x16
        convRelu(6, True)  # 512x1x16
        # print(convRelu)
        self.cnn = cnn

        self.rnn = nn.Sequential(
            BidirectionalLSTM(576, nh, nh),
            BidirectionalLSTM(nh, nh, nclass))
        
        # 7680
        # self.rnn = nn.Sequential(
        #     BidirectionalLSTM(1920, nh, nh),
        #     BidirectionalLSTM(nh, nh, nclass))
        # self.rnn = nn.Sequential(
        #     BidirectionalLSTM(1792, nh, nh),
        #     BidirectionalLSTM(nh, nh, nclass))
        # self.rnn = nn.Sequential(
        #     BidirectionalLSTM(512, nh, nh),
        #     BidirectionalLSTM(nh, nh, nclass))

    def forward(self, input):
        # conv features
        # print('---forward propagation---')
        conv = self.cnn(input)              #[8, 512, 15, 301]
        # print(conv.size())
        b, c, h, w = conv.size()  # /1*512*1*48

        conv = conv.reshape((b, c * h, 1, w))
        # print('conv.size()',conv.size())

        b, c, h, w = conv.size()  # /1*512*1*48
        assert h == 1, "the height of conv must be 1"
        conv = conv.squeeze(2)  # b *c * width  /1*512*48
        # print('conv.shape:',conv.shape)
        conv = conv.permute(2, 0, 1)  # [w, b, c] #48*1*512
        # self.rnn(conv).shape #48*1*nclass
        output = F.log_softmax(self.rnn(conv), dim=2)
        # print('output.shape:',output.shape)#48*1*nclass
        # print('output:',output[:,:,2])
        return output

    def backward_hook(self, module, grad_input, grad_output):
        for g in grad_input:
            g[g != g] = 0  # replace all nan/inf in gradients to zero
