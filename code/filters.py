from opencv.cv import *
from config import cam_resolution as res

# a simple wrapper for the OpenCV Kalman filter
class Kalman:
	def __init__(self, initial_val=[0], p_noise=[1e-2], m_noise=[1e-3], m_mat=[1], ecv=[1]):
		self.kalman = cvCreateKalman( len(initial_val), len(initial_val), 0 )
		self.measurement = cvCreateMat( len(initial_val), 1, CV_32FC1 )
		self.prediction = None
		cvZero( self.measurement )
		cvSetIdentity( self.kalman.measurement_matrix, cvRealScalar(*m_mat) )
		cvSetIdentity( self.kalman.process_noise_cov, cvRealScalar(*p_noise) )
		cvSetIdentity( self.kalman.measurement_noise_cov, cvRealScalar(*m_noise) )
		cvSetIdentity( self.kalman.error_cov_post, cvRealScalar(*ecv))
		for v in initial_val:
		    self.kalman.state_post[initial_val.index(v), 0] = v
		    self.kalman.state_pre[initial_val.index(v), 0] = v

	def get_prediction(self):
		self.prediction = cvKalmanPredict( self.kalman )
		return self.prediction
	
	def correct(self, *corrections):
	    if self.prediction:
	        self.measurement = self.prediction
	    for c in corrections:
	        self.measurement[corrections.index(c), 0] = c
		cvKalmanCorrect( self.kalman,  self.measurement)


#NOTE: face length Kalman filtering is only used on the frontal faces that are detected
face = Kalman(initial_val=[res[0] / 2, res[1] / 2, 140])

