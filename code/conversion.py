import cv
from pygame import surfarray

"""
These decorators could pass on other function args...
something like: *args=None, **argd=None
"""

class numpyFromSurf(object):
    """This decorator can be used to wrap a function that takes 
    and returns a numpy array into one that takes and retuns a
    pygame surface.
    """
    def __init__(self, f):
        self.f = f  
    
    def __call__(self, imageSurface):
        # Convert surface to ndarray - could also directly acess pixels...
        np_image = surfarray.array3d(imageSurface)
        
        # Call the original function
        np_image_filtered = self.f(np_image)
        
        # Convert back to surface
        return surfarray.make_surface(np_image_filtered)
        
try:
    from opencv import adaptors
    
    class numpyFromOpenCV(object):
        """This decorator can be used to wrap a function that takes 
        and returns a numpy array into one that takes and retuns an
        opencv CvMat. If the orrientation matters we might need to 
        transpose (1,0,2)
        """
        def __init__(self, f):
            self.f = f    
    
        def __call__(self, image):
            # Convert CvMat to ndarray
            np_image = adaptors.Ipl2NumPy(image)
            
            # Call the original function
            np_image_filtered = self.f(np_image)
            
            # Convert back to CvMat
            return adaptors.NumPy2Ipl(np_image_filtered)
    
    def surf2CV(surf):
        """
        Given a Pygame surface, convert to an OpenCv cvArray format.
        Either Ipl image or cvMat.
        """
        
        
        numpyImage = surfarray.pixels3d(surf)#.copy()    # Is this required to be a copy?
        cvImage = adaptors.NumPy2Ipl(numpyImage.transpose(1,0,2))
        
        
        
        '''arr = surfarray.pixels3d(surf)
        
        w = int(surf.get_width())
        h = int(surf.get_height())
        
        print str(w) + " " + str(h)
        
        cvImage = cv.CreateImage((w,h), 8, 3)

        #cvSet(cvImage, (0,0,0))
        #print arr[0][0][0]
        
        for x in range(200):
            for y in range(200):
                cv.Set2D(cvImage, y, x, (int(arr[y][x][0]), int(arr[y][x][1]), int(arr[y][x][2])))'''
                
        return cvImage
        

    def cv2SurfArray(cvMat):
        """Given an open cvMat convert it to a pygame surface pixelArray
        Should be able to call blit_array directly on this.
        """
        numpyImage = adaptors.Ipl2NumPy(cvMat)
        return numpyImage.transpose(1,0,2)

    
except ImportError:
    pass

try:

    import cv

    def cv2array(im):
        depth2dtype = {
            cv.IPL_DEPTH_8U: 'uint8',
            cv.IPL_DEPTH_8S: 'int8',
            cv.IPL_DEPTH_16U: 'uint16',
            cv.IPL_DEPTH_16S: 'int16',
            cv.IPL_DEPTH_32S: 'int32',
            cv.IPL_DEPTH_32F: 'float32',
            cv.IPL_DEPTH_64F: 'float64',
        }

        arrdtype=im.depth
        a = np.fromstring(
        im.tostring(),
        dtype=depth2dtype[im.depth],
        count=im.width*im.height*im.nChannels)
        a.shape = (im.height,im.width,im.nChannels)
        return a

    def array2cv(a):
        dtype2depth = {
            'uint8': cv.IPL_DEPTH_8U,
            'int8': cv.IPL_DEPTH_8S,
            'uint16': cv.IPL_DEPTH_16U,
            'int16': cv.IPL_DEPTH_16S,
            'int32': cv.IPL_DEPTH_32S,
            'float32': cv.IPL_DEPTH_32F,
            'float64': cv.IPL_DEPTH_64F,
        }
        try:
            nChannels = a.shape[2]
        except:
            nChannels = 1
        cv_im = cv.CreateImageHeader((a.shape[1],a.shape[0]),
        dtype2depth[str(a.dtype)], nChannels)
        cv.SetData(cv_im, a.tostring(),a.dtype.itemsize*nChannels*a.shape[1])
        return cv_im
except:
    pass
