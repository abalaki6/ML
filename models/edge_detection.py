import numpy as np
from scipy.misc import imread, imsave
import matplotlib.pyplot as plt
from time import time

def get_edge_detected_images(image, sob_mode='constant'):    
    '''
        Take the the image and return 1 image with edge detections
        @param image the image that we want to detect edges
        @param sob_mode the sob borders adjustment mode
        @return sob_image
    '''
    sx = ndimage.sobel(image, axis=0, mode=sob_mode)
    sy = ndimage.sobel(image, axis=1, mode=sob_mode)
    return np.hypot(sx, sy)



def usage_example():
    imgname = 'canny4'

    im = np.array(imread('../images/' + imgname + '.jpg',mode='P'),dtype=float)
    t1 = time()
    sob = get_edge_detected_images(im)
    t2 = time()
    print("time of execution: ", t2 - t1)

    plt.imshow(sob, cmap='gray')
    plt.show()
    imsave('../images/' + imgname + 'edge.jpg', sob)
