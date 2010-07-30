import cv
from config import cam_resolution as res

# a simple wrapper for the OpenCV Kalman filter
class Kalman:
	def __init__(self, initial_val=0, p_noise=1e-2, m_noise=1e-3, error=1):
		self.kalman = cv.CreateKalman( 1, 1, 0 )
		self.measurement = cv.CreateMat( 1, 1, cv.CV_32FC1)
		self.initial_state = cv.CreateMat( 1, 1, cv.CV_32FC1)
		self.prediction = None
		cv.SetZero( self.measurement )
		self.measurement[0,0] = initial_val
		self.initial_state[0,0] = initial_val
		cv.SetIdentity( self.kalman.measurement_matrix, cv.RealScalar(1) )
		cv.SetIdentity( self.kalman.process_noise_cov, cv.RealScalar(p_noise) )
		cv.SetIdentity( self.kalman.measurement_noise_cov, cv.RealScalar(m_noise) )
		cv.SetIdentity( self.kalman.error_cov_post, cv.RealScalar(error))
		self.kalman.state_post[0,0] = initial_val
		self.kalman.state_pre[0,0] = initial_val

	def get_prediction(self):
		self.prediction = cv.KalmanPredict( self.kalman )
		return self.prediction[0,0] 
	
	def correct(self, correction):
		self.measurement[0,0] = correction
		cv.KalmanCorrect( self.kalman,  self.measurement)


#NOTE: face length Kalman filtering is only used on the frontal faces that are detected
face_x = Kalman(res[0] / 2) #face x location kalman filter
face_y = Kalman(res[1] / 2) #face y location kalman filter
face_l = Kalman(140) #face length kalman filter
