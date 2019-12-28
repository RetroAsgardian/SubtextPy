#!/usr/bin/env python3
"""
SubtextPy - Official client API for Subtext.
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

class Client:
	"""
	Subtext Client API class.
	"""
	def __init__(self, url: str):
		self.url = url.rstrip("/")
		
		# Check for a valid Subtext instance
		resp = requests.get(self.url)
		if resp.status_code != 200 or resp.text.strip().capitalize() != "Subtext":
			raise ValueError("Could not detect a valid Subtext instance at {}".format(self.url))
	
	def _request(self, method: str, url: str, **kwargs):
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
	
	def _get(self, url: str, **kwargs):
		return self._request('GET', url, **kwargs)
	def _post(self, url: str, **kwargs):
		return self._request('POST', url, **kwargs)
	def _put(self, url: str, **kwargs):
		return self._request('PUT', url, **kwargs)
	def _patch(self, url: str, **kwargs):
		return self._request('PATCH', url, **kwargs)
	def _delete(self, url: str, **kwargs):
		return self._request('DELETE', url, **kwargs)
	
	def about(self):
		"""
		Retrieve server info.
		"""
		return self._get("/Subtext").json()
		
	
	def login(self, user_id: Optional[UUID], password: str, *, username: Optional[str] = None):
		"""
		Log in as the specified user.
		"""
		if user_id is None:
			if username is None:
				raise ValueError("Must specify user ID or username")
			
			# Get user ID
			resp = self._get("/Subtext/user/queryidbyname", params={
				'name': username
			})
			user_id = UUID(resp.json())
		
		resp = self._post("/Subtext/user/login", params={
			'userId': user_id,
			'password': password
		})
		
		return Session(UUID(resp.json()), user_id, self)

class Session:
	"""
	A Subtext user session.
	"""
	def __init__(self, id: UUID, user_id: UUID, client: Client):
		self._client: Client = client
		
		self.id: UUID = id
		self.user_id: UUID = user_id
	
	def heartbeat(self):
		"""
		Keep this session from expiring.
		"""
		self._client._post("/Subtext/user/hearbeat", params={
			'sessionId': self.id
		})
	
	def logout(self):
		"""
		Log out of this session.
		"""
		self._client._post("/Subtext/user/logout", params={
			'sessionId': self.id
		})
		self.id = None
		self.user_id = None
	
	def get_user(self, user_id: UUID):
		"""
		Retrieve a user.
		"""
		resp = self._client._get("/Subtext/user/{}".format(user_id), params={
			'sessionId': self.id,
			'userId': user_id
		})
		
		# TODO convert to User object
		return resp.json()
