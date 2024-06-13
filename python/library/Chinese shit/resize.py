import cv2
import numpy as np

def resize_padding_im(im, output_size):
    trans_size = np.asarray(output_size)
    h, w, _ = im.shape
    temp_im = np.zeros((*output_size, 3))
    input_size = np.asarray((h, w))
    sclaes = trans_size / input_size
    min_scale = np.amin(sclaes)
    if input_size[0] > input_size[1]:
        new_w = int(w * min_scale)
        half_cape = (output_size[0] - new_w)//2
        im = cv2.resize(im, (new_w, round(h * min_scale)))
        temp_im[:, half_cape: half_cape + new_w] = im[:, :, :]
    else:
        new_h = int(h * min_scale)
        half_cape = (output_size[1] - new_h) // 2
        im = cv2.resize(im, (round(w * min_scale), new_h))
        temp_im[half_cape: half_cape + new_h, :] = im[:, :, :]
    return temp_im



