import numpy as np
import tensorflow as tf

from time import time
import matplotlib.pyplot as plt
flags = tf.app.flags.FLAGS

class CNN:

	@staticmethod
	def load_model(source, label):
		'''
			load model from file
		'''
		model = CNN(label)
		model.load(source)
		return model

	def __init__(self, label):
		self.label = label
		config = tf.ConfigProto()
		config.gpu_options.allow_growth = True
		self.session = tf.Session(config=config)
		self.create_graph_segmentation()
		self.configurate()

	def save(self, model_file):
		'''
			@param model_file destination path
		'''
		self.saver = tf.train.Saver()
		self.saver.save(self.session, model_file)
		

	def load(self, model_file):
		'''
			@param model_file source of model path
		'''
		self.saver = tf.train.Saver()
		print(model_file)
		self.saver.restore(self.session, model_file)
		print('done')


	def fit(self, X, Y):
		'''
			train the tf graph model here 
			@param X input tensor 
			@param Y ouput tensor
		'''
		for i in range(flags.num_steps):
			self.session.run(self.optimize, feed_dict={self.X: X, self.Y:Y})
	
	def configurate(self):
		'''
			sets up global variables and seed for tf environment
		'''
		init = tf.global_variables_initializer()
		self.session.run(init)


	def create_graph_segmentation(self):
		'''
			creates tf graph for segmentation analysis 
		'''
		# get dimensional variables
		ch = flags.num_channels
		w = flags.width
		h = flags.height
		batch_size = flags.batch_size
		# create tuplex with input image size
		input_shape = (batch_size, h, w, ch)
		# define placeholders for input and output tensors
		self.X = tf.placeholder(tf.float32, shape=input_shape, name='X')
		self.Y = tf.placeholder(tf.float32, shape=(batch_size, w*h), name='Y')
		# define fisrt convolution
		self.W1_shape = (5, 5, ch, 15)
		self.W1_init = init_filter_weight(self.W1_shape)
		self.b1_init = init_bias(self.W1_shape[-1])
		# define variable in tf
		self.W1 = tf.Variable(self.W1_init.astype(np.float32), name='W1')
		self.b1 = tf.Variable(self.b1_init.astype(np.float32), name='b1')
		self.Z1 = convpool(self.X, self.W1, self.b1)
		# define second convolution
		self.W2_shape = (5, 5, self.W1_shape[-1], 30)
		self.W2_init = init_filter_weight(self.W2_shape)
		self.b2_init = init_bias(self.W2_shape[-1])
		# define variable in tf
		self.W2 = tf.Variable(self.W2_init.astype(np.float32), name='W2')
		self.b2 = tf.Variable(self.b2_init.astype(np.float32), name='b2')
		self.Z2 = convpool(self.Z1, self.W2, self.b2)
		# define 3rd convolution
		self.W3_shape = (10, 10, self.W2_shape[-1], 70)
		self.W3_init = init_filter_weight(self.W3_shape)
		self.b3_init = init_bias(self.W3_shape[-1])
		# define variable in tf
		self.W3 = tf.Variable(self.W3_init.astype(np.float32), name='W3')
		self.b3 = tf.Variable(self.b3_init.astype(np.float32), name='b3')
		self.Z3 = convpool(self.Z2, self.W3, self.b3)


		# define fc layer TODO: calculate the input size
		self.W4_init = init_weight(87500, 1024)
		self.b4_init = init_bias(1024)
		# define in tf
		self.W4 = tf.Variable(self.W4_init.astype(np.float32), name='W4')
		self.b4 = tf.Variable(self.b4_init.astype(np.float32), name='b4')
		# flatter the current flow
		self.Z3_shape = self.Z3.get_shape().as_list()
		# Z2_shape[0] is number of samples in tensor4D, the rest are flatten
		self.Z3f = tf.reshape(self.Z3, [self.Z3_shape[0], np.prod(self.Z3_shape[1:])])
		self.Z4 = tf.nn.sigmoid(tf.matmul(self.Z3f, self.W4) + self.b4, name='Z4')

	
		# define second fc layer
		self.W5_init = init_weight(1024, w * h)
		self.b5_init = init_bias(w * h)
		# add to tf
		self.W5 = tf.Variable(self.W5_init.astype(np.float32), name='W5')
		self.b5 = tf.Variable(self.b5_init.astype(np.float32), name='b5')
		self.Z5 = tf.matmul(self.Z4, self.W5) + self.b5
		self.y_hat = tf.nn.sigmoid(self.Z5, name='y_hat')
		# prediction, cost,  optimazer
		#def prediction():
			#return tf.cast(self.y_hat + 0.2, tf.int32)
			#return tf.reshape(labels, [batch_size, h, w], name='prediction')
		self.predict = tf.cast(self.y_hat + 0.2, tf.int32, name='predict')
		#self.cost = tf.reduce_mean(-tf.reduce_sum(self.Y * tf.log(self.y_hat), reduction_indices=1))
		#self.optimizer = tf.train.RMSPropOptimizer(learning_rate=flags.learning_rate,
		# momentum=flags.momentum, decay=flags.decay).minimize(self.cost)
		self.cost = tf.reduce_mean(-tf.reduce_sum(self.Y * tf.log(self.y_hat)),name='cost')
		self.optimize = tf.train.RMSPropOptimizer(learning_rate=flags.learning_rate,
		 momentum=flags.momentum, decay=flags.decay).minimize(self.cost,name='optimize')

		# separate for single prediction TODO MAKE IT NACE TO WORK WITH TF
		input_shape = (1, h, w, ch)
		# define placeholders for input and output tensors
		self.Z = tf.placeholder(tf.float32, shape=input_shape, name='Z')
		self.c1 = convpool(self.Z,self.W1,self.b1)
		self.c2 = convpool(self.c1,self.W2,self.b2)
		self.c3 = convpool(self.c2,self.W3,self.b3)
		self.c3_shape = self.c3.get_shape().as_list()
		# Z2_shape[0] is number of samples in tensor4D, the rest are flatten
		self.c3f = tf.reshape(self.c3, [1, np.prod(self.c3_shape[:])])
		self.c4 = tf.nn.sigmoid(tf.matmul(self.c3f, self.W4) + self.b4)
		self.c5 = tf.matmul(self.c4, self.W5) + self.b5
		self.cy_hat = tf.nn.sigmoid(self.c5)
		self.cpredict = tf.cast(self.cy_hat + 0.2, tf.int32)
			

	def calculate_cost(self, X, Y):
		return self.session.run(self.cost, feed_dict={self.X:X, self.Y:Y})
		
	def predict_label(self,X):
		'''
			performs inference
			@param X input tensor
			@return Y predicting output
		'''
		if len(X.shape) == 4:
			p = self.session.run(self.predict, feed_dict={self.X: X})
			p = np.reshape(p,(flags.batch_size, flags.height, flags.width))
		else:
			p = self.session.run(self.cpredict, feed_dict={self.Z:np.array([X])})
			p = np.reshape(p, (flags.height, flags.width))
		return p


def convpool(X, W, b):
	'''
		default maxpool size is (2,2)
		@param X input tensor
		@param W convolution weight matrix
		@param b bias for convolution result
		@return biased convolution result
	'''
	conv_out = tf.nn.conv2d(X, W, strides=[1, 1, 1, 1], padding='SAME')
	conv_out = tf.nn.bias_add(conv_out, b)
	pool_out = tf.nn.max_pool(conv_out, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
	return tf.nn.relu(pool_out)


def init_filter_weight(shape):
	'''
		@param shape the shape of the filter
		@return normal random filter with shape shape
	'''
	return np.random.randn(*shape) / np.sqrt(2 / np.prod(shape[:-1]), dtype=np.float32)


def init_weight(M, K):
	'''
		@param M input size
		@param K output size
		@return normal random matrix (M,K)
	'''
	return np.random.randn(M, K) / np.sqrt(M + K)


def init_bias(size):
	'''
		@param size of the bias vector
		@return zero vector of size size
	'''
	return np.zeros(size, dtype=np.float32)

