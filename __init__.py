#!/usr/bin/env python3
"""
SubtextPy - Official client API for Subtext.
"""
import requests

class APIError(Exception):
	"""
	Generic API error.
	"""
	def __init__(self, message: str, status_code: int):
		self.message = message
		self.status_code = status_code

class Subtext:
	def __init__(self, url: str):
		self.url = url.rstrip("/")
		
		# Check for a valid Subtext instance
		resp = requests.get(self.url)
		if resp.status_code != 200 or resp.text.strip().capitalize() != "Subtext":
			raise ValueError("Could not detect a valid Subtext instance at {}".format(self.url))
		
	def about(self):
		"""
		Retrieve server info.
		"""
		resp = requests.get(self.url + "/Subtext")
		if resp.status_code // 100 != 2:
			if resp.headers['Content-Type'] == 'application/json':
				raise APIError(resp.json()['error'], resp.status_code)
			else:
				raise APIError(resp.text, resp.status_code)
		return resp.json()
