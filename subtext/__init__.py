#!/usr/bin/env python3
"""
subtext - Official Python client API for Subtext.
"""
from .common import APIError, ContextError, Context
from uuid import UUID
from datetime import datetime
from typing import Optional, Union
import iso8601

class Client:
	"""
	Subtext Client API class.
	"""
	def __init__(self, url: str):
		self.ctx = Context(url)
		
		# Check for a valid Subtext instance
		resp = self.ctx.get('/')
		if resp.status_code != 200 or resp.text.strip().capitalize() != "Subtext":
			raise ValueError("Could not detect a valid Subtext instance at {}".format(self.ctx.url))
	
	def login(self, user: Union[UUID, str], password: str):
		"""
		Log in with the given credentials.
		"""
		if self.ctx._session_id is not None or self.ctx._user_id is not None:
			raise ContextError("Context is already associated with a session, try logging out")
		
		if isinstance(user, UUID):
			user_id = user
		else:
			user_id = self.ctx.get('/Subtext/user/queryidbyname', params={
				'name': user
			}).json()
		
		session_id = self.ctx.post('/Subtext/user/login', params={
			'userId': user_id,
			'password': password
		}).json()
		
		self.ctx._session_id = session_id
		self.ctx._user_id = user_id
	
	def logout(self):
		"""
		Log out of the current session.
		"""
		self.ctx.post('/Subtext/user/logout', params={
			'sessionId': self.ctx.session_id()
		})
		
		self.ctx._session_id = None
		self.ctx._user_id = None
