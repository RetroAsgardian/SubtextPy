#!/usr/bin/env python3
"""
subtext - Official Python client API for Subtext.
"""
import requests
from uuid import UUID
from enum import Enum
from typing import Optional, Callable, List, Any
from datetime import datetime
import iso8601
import collections

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
		self._client = client
		
		self.id = id
		self.user = self.get_user(user_id)
	
	def heartbeat(self):
		"""
		Keep this session from expiring.
		"""
		self._client._post("/Subtext/user/heartbeat", params={
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
	
	def _get_user(self, user_id: UUID):
		resp = self._client._get("/Subtext/user/{}".format(user_id), params={
			'sessionId': self.id,
			'userId': user_id
		})
		
		return resp.json()
	
	def _get_user_friends(self, user_id: UUID, start: Optional[int] = None, count: Optional[int] = None):
		resp = self._client._get("/Subtext/user/{}/friends".format(user_id), params={
			'sessionId': self.id,
			'userId': user_id,
			'start': start,
			'count': count
		})
		
		return resp.json()
	
	def _get_user_blocked(self, user_id: UUID, start: Optional[int] = None, count: Optional[int] = None):
		resp = self._client._get("/Subtext/user/{}/blocked".format(user_id), params={
			'sessionId': self.id,
			'userId': user_id,
			'start': start,
			'count': count
		})
		
		return resp.json()
	
	def get_user(self, user_id: UUID):
		"""
		Retrieve a user.
		"""
		user = User(user_id, self)
		user.refresh()
		return user


class SubtextObj:
	"""
	An object that exists on a Subtext instance, referenced by a UUID.
	"""
	def __init__(self, id: UUID, context=None):
		self.id = id
		self._context = context
	
	def refresh(self):
		"""
		Update the object with the latest available data from the instance.
		"""
		raise NotImplementedError()

class UserPresence(Enum):
	offline = "Offline"
	online = "Online"
	away = "Away"
	busy = "Busy"

class PagedList(collections.abc.Iterable):
	"""
	Iterable that retrieves chunks of values from a function.
	"""
	def __init__(self, callback: Callable[[int], List[SubtextObj]]):
		self._callback = callback
		self._list = []
	def __getitem__(self, index: int) -> Any:
		if not isinstance(index, int):
			raise TypeError("index must be int")
		while index >= len(self._list):
			if not self.__fetch():
				raise IndexError("index out of range")
		return self._list[index]
	def __iter__(self) -> Any:
		for item in self._list:
			yield item
		start = len(self._list)
		while True:
			page = self._callback(start)
			if len(page) <= 0:
				break
			for item in page:
				if not any(x.id == item.id for x in self._list):
					self._list.append(item)
					start += 1
				yield item
	def __fetch(self) -> bool:
		page = self._callback(self, len(self._list))
		if len(page) <= 0:
			return False
		for item in page:
			if not any(x.id == item.id for x in self._list):
				self._list.append(item)
		return True

class User(SubtextObj):
	"""
	Represents a Subtext user.
	"""
	def __init__(self, id: UUID, context: Optional[Session] = None, **kwargs):
		super().__init__(id, context)
		
		self.name = kwargs.get('name', None)
		
		self.presence = kwargs.get('presence', None)
		self.last_active = kwargs.get('last_active', None)
		self.status = kwargs.get('status', None)
		
		self.is_deleted = kwargs.get('is_deleted', None)
		
		self.blocked = kwargs.get('blocked', None)
		self.friends = kwargs.get('friends', None)
		self.friend_requests = kwargs.get('friend_requests', None)
		self.keys = kwargs.get('keys', None)
	
	def refresh(self):
		if self._context is None:
			return
		
		data = self._context._get_user(self.id)
		
		self.name = data['name']
		
		if 'presence' in data:
			self.presence = UserPresence(data['presence'])
		if 'lastActive' in data:
			self.last_active = iso8601.parse_date(data['lastActive'])
		if 'status' in data:
			self.status = data['status']
		
		self.is_deleted = data['isDeleted']
		
		def friends_page(start: int) -> List[SubtextObj]:
			data = self._context._get_user_friends(self.id, start)
			return [User(user_id, self._context) for user_id in data]
		
		self.friends = PagedList(friends_page)
