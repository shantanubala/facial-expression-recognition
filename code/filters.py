from opencv.cv import *
from config import cam_resolution as res

# a simple wrapper for the OpenCV Kalman filter
class Kalman:
	def __init__(self, initial_val=0, p_noise=1e-2, m_noise=1e-3, error=1):
		self.kalman = cvCreateKalman( 1, 1, 0 )
		self.measurement = cvCreateMat( 1, 1, CV_32FC1 )
		self.initial_state = cvCreateMat( 1, 1, CV_32FC1 )
		self.prediction = None
		cvZero( self.measurement )
		self.measurement[0,0] = initial_val
		self.initial_state[0,0] = initial_val
		cvSetIdentity( self.kalman.measurement_matrix, cvRealScalar(1) )
		cvSetIdentity( self.kalman.process_noise_cov, cvRealScalar(p_noise) )
		cvSetIdentity( self.kalman.measurement_noise_cov, cvRealScalar(m_noise) )
		cvSetIdentity( self.kalman.error_cov_post, cvRealScalar(error))
		self.kalman.state_post[0,0] = initial_val
		self.kalman.state_pre[0,0] = initial_val

	def get_prediction(self):
		self.prediction = cvKalmanPredict( self.kalman )
		return self.prediction[0,0] 
	
	def correct(self, correction):
		self.measurement[0,0] = correction
		cvKalmanCorrect( self.kalman,  self.measurement)


#NOTE: face length Kalman filtering is only used on the frontal faces that are detected
face_x = Kalman(res[0] / 2) #face x location kalman filter
face_y = Kalman(res[1] / 2) #face y location kalman filter
face_l = Kalman(140) #face length kalman filter
