# -*- coding: utf-8 -*-

import torch


class strLabelConverter(object):
    """Convert between str and label.

    NOTE:
        Insert `blank` to the alphabet for CTC.

    Args:
        alphabet (str): set of the possible characters.
        ignore_case (bool, default=True): whether or not to ignore all of the case.
    """

    def __init__(self, phoneme_list):
        self.phoneme_dict = {}
        self.num_dict = {}

        for i, char in enumerate(phoneme_list):
            # NOTE: 0 is reserved for 'blank' required by wrap_ctc
            self.phoneme_dict[char] = i
            self.num_dict[i] = char

    def encodePhn(self, text):
        # text a string tuple
        """Support batch or single str.

        Args:
            text (str or list of str): texts to convert.

        Returns:
            torch.IntTensor [length_0 + length_1 + ... length_{n - 1}]: encoded texts.
            torch.IntTensor [n]: length of each text.
        """
        length = []
        result = []
        decode_flag = True if type(text[0]) == bytes else False

        for item in text:
            if decode_flag:
                item = item.decode('utf-8', 'strict')

            phm = item.split(' ')

            length.append(len(phm))
            for cnt in phm:
                try:
                    # length.append(len(cnt))
                    index = self.phoneme_dict[cnt]
                    result.append(index)
                except:
                    txt = '<SIL>'
                    index = self.phoneme_dict[txt]
                    result.append(index)
                    
        
        return (torch.IntTensor(result), torch.IntTensor(length))

    def decodePhn(self, t, length, raw=False):
        """Decode encoded texts back into strs.
        # preds.data, preds_size.data, raw=True
        # 301*bach_size, batch_size
        
        Args:
            torch.IntTensor [length_0 + length_1 + ... length_{n - 1}]: encoded texts.
            torch.IntTensor [n]: length of each text.

        Raises:
            AssertionError: when the texts and its length does not match.

        Returns:
            text (str or list of str): texts to convert.
            
        """
        texts = []
        addr = []
        slength=0

        for j in range(length.numel()):            
            datalength = length[j].item()
            # print(slength)
            if raw:
                return ''.join([self.phoneme_dict[j - 1] for j in t])
            else:
                char_list = []
                char_addr = []
                for i in range(slength, slength+datalength):
                    # if t[i] != 0 and (not (i > 0 and t[i - 1] == t[i])):
                    if t[i] != 0 and (i>0 and t[i] != t[i-1]) :    
                        char_list.append(self.num_dict[t[i].item()])
                        char_addr.append(i)
                    # else:
                    #     print('decode error. ')
                    #     print(t[i])
                # return ''.join(char_list)
                slength = slength+datalength
                
                texts.append(' '.join(char_list))
                addr.append(char_addr)
   
        return texts, addr


if __name__ == '__main__':
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    converter = strLabelConverter(alphabet)
