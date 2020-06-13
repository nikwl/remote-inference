import zmq
import numpy as np
from imagezmq import imagezmq

class Streamer():
	def _start_image_hub(self, incoming_socket='5555'):
		self.imageHub = imagezmq.ImageHub(open_port='tcp://*:' + str(incoming_socket))
		print('Connected to incoming stream at: ' + 'tcp://*:' + str(incoming_socket))

	def _start_image_sender(self, outgoing_addr, outgoing_socket='5555'):
		self.sender = imagezmq.ImageSender(connect_to="tcp://{}:".format(outgoing_addr) + str(outgoing_socket))
		print("Connected to outgoing stream at: " + "tcp://{}:".format(outgoing_addr) + str(outgoing_socket))

	def accept(self, client_addr='localhost', server_port='5555', client_port='5557'):
		'''
			accept: Opens a zmq socket server side. See imagezmq 
				documentation for details.
		'''

		self._start_image_sender(client_addr, server_port)
		self._start_image_hub(client_port)

	def connect(self, server_addr='localhost', server_port='5555', client_port='5557'):
		'''
			connect: Opens a zmq socket client side. See imagezmq 
				documentation for details.
		'''
		self._start_image_sender(server_addr, client_port)
		self._start_image_hub(server_port)
		try:
			self.imageHub.send_reply(b'OK')
		except zmq.error.ZMQError:
			pass

	def get_frame(self):
		'''
			get_frame: Get the next frame or frames from the client. Unpack the frames 
				in the same format that you sent them. 
		'''

		try:
			# Get the next frame
			image_shapes, frames_padded = self.imageHub.recv_image()
			self.imageHub.send_reply(b'OK')

			# Reform the frame based on the passed frame sizes
			frames = []
			i = 0
			for sh, f in zip(image_shapes, frames_padded):
				h, w, c = sh
				frames.append(frames_padded[:h, :w, i:i+c])
				i += c
				
			return frames
		except KeyboardInterrupt:
			exit(0)

	def send_frame(self, frames):
		'''
			send_image: Send a frame or list of frames to the server. Unpack the frames on 
				the server side in the same format that you sent them. 
			ARGUMENTS:
				frames: 2d image OR 3d image OR a list of any 2d or 3d images. 
					A single cv2 image or list of images.
		'''
		try:
			# Input is a list of images
			if isinstance(frames, list):
				image_shapes = [f.shape if f.ndim == 3 else tuple(list(f.shape) + [1]) for f in frames]

				# Determine the size of the largest image to be sent
				max_sh = [1, 1]
				for sh in image_shapes:
					max_sh = [max(max_sh[0], sh[0]), max(max_sh[1], sh[1])]

				frames_padded = []
				for sh, f in zip(image_shapes, frames):
					h, w, c = sh

					# 2d images need to be expanded
					if f.ndim == 2:
						f = np.expand_dims(f, axis=2)
					
					# Create a padded image equal to the size of the largest image
					f_pad = np.zeros(max_sh + [c], dtype=np.uint8)
					f_pad[:h, :w, :c] = f

					frames_padded.append(f_pad)
				frames_padded = np.concatenate(frames_padded, axis=2)

			# Input is a single image
			else:
				frames_padded = frames
				if frames.ndim == 2:
					image_shapes = [tuple(list(frames.shape) + [1])]
				else:
					image_shapes = [frames.shape]

			# Send the concatonated images
			self.sender.send_image(image_shapes, frames_padded)
		except KeyboardInterrupt:
			exit(0)
