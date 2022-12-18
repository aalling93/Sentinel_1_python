from scipy import ndimage
import numpy as np
#

def boxcar(img, kernel_size, **kwargs):
    """Simple (kernel_size x kernel_size) boxcar filter.
    Args:
        img(2d numpy array): image
        kernel_size(int): size of kernel
        **kwargs: Additional arguments passed to scipy.ndimage.convolve
    Returns:
        Filtered image
    Raises:
    """
    # For small kernels simple convolution
    if kernel_size < 8:
        kernel = np.ones([kernel_size, kernel_size])
        box_img = ndimage.convolve(img, kernel, **kwargs) / kernel_size**2

    # For large kernels use Separable Filters. (https://www.youtube.com/watch?v=SiJpkucGa1o)
    else:
        kernel1 = np.ones([kernel_size, 1])
        kernel2 = np.ones([1, kernel_size])
        box_img = ndimage.convolve(img, kernel1, **kwargs) / kernel_size
        box_img = ndimage.convolve(box_img, kernel2, **kwargs) / kernel_size

    return box_img
