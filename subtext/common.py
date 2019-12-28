#!/usr/bin/env python3
"""
subtext.common
"""
import requests
from uuid import UUID
from typing import Optional

class APIError(Exception):
	"""
	Generic API error.
	"""
	def __init__(self, message: str, status_code: int, **other_data):
		self.message = message
		self.status_code = status_code
		self.other_data = other_data

class ContextError(Exception):
	"""
	Generic context error.
	"""

class Context:
	"""
	Stores Subtext client context information.
	"""
	def __init__(self, url: str, *, session_id: Optional[UUID] = None, user_id: Optional[UUID] = None):
		self.url = url.rstrip("/")
		self._session_id = session_id
		self._user_id = user_id
	def session_id(self):
		"""
		Retrieve the associated session ID, or raise a ContextError if there is none.
		"""
		if self._session_id is None:
			raise ContextError("Context is not associated with a session, try logging in")
		return self._session_id
	def user_id(self):
		"""
		Retrieve the associated user ID, or raise a ContextError if there is none.
		"""
		if self._user_id is None:
			raise ContextError("Context is not associated with a session, try logging in")
		return self._user_id
	
	def request(self, method: str, url: str, **kwargs):
		"""
		Send an HTTP request.
		"""
		resp = requests.request(method, self.url + url, **kwargs)
		
		# Handle error
		if resp.status_code // 100 != 2:
			if resp.headers.get('Content-Type', None) == 'application/json':
				errdata = resp.json()
				errmsg = errdata.pop('error')
				raise APIError(errmsg, resp.status_code, **errdata)
			else:
				raise APIError(resp.text, resp.status_code)
		
		return resp
	
	def get(self, url: str, **kwargs):
		"""
		Send an HTTP GET request.
		"""
		return self._request('GET', url, **kwargs)
	def post(self, url: str, **kwargs):
		"""
		Send an HTTP POST request.
		"""
		return self._request('POST', url, **kwargs)
	def put(self, url: str, **kwargs):
		"""
		Send an HTTP PUT request.
		"""
		return self._request('PUT', url, **kwargs)
	def patch(self, url: str, **kwargs):
		"""
		Send an HTTP PATCH request.
		"""
		return self._request('PATCH', url, **kwargs)
	def delete(self, url: str, **kwargs):
		"""
		Send an HTTP DELETE request.
		"""
		return self._request('DELETE', url, **kwargs)
