#!/usr/bin/env python3
"""
subtext.common
"""
import requests
from uuid import UUID
from typing import Optional
import iso8601
import re

# https://stackoverflow.com/a/1176023 - camelCase to snake_case
_RE_SNAKE_CASE = re.compile(r'(?<!^)(?=[A-Z])')
def snake_case(name: str) -> str:
	"""
	Convert camelCase or PascalCase into snake_case
	"""
	return _RE_SNAKE_CASE.sub('_', name).lower()

class APIError(Exception):
	"""
	Generic API error.
	"""
	def __init__(self, message: str, status_code: int, **data):
		self.message = message
		self.status_code = status_code
		self.__dict__.update({snake_case(key): data[key] for key in data})

class AuthError(APIError):
	"""
	Generic authentication error.
	"""

class AdminLoggedIn(APIError):
	"""
	Admin already has an active session elsewhere.
	"""

class AdminLoggedOut(APIError):
	"""
	Admin has logged out.
	"""

class IncorrectResponse(APIError):
	"""
	Incorrect response was given for admin challenge-response login.
	"""

class UserLocked(APIError):
	"""
	User account is locked.
	"""
	def __init__(self, message: str, status_code: int, **data):
		super().__init__(message, status_code, **data)
		self.lock_expiry = iso8601.parse_date(self.lock_expiry)

class SessionExpired(APIError):
	"""
	Session has expired.
	"""

class NoObjectWithId(APIError):
	"""
	Object does not exist on the server.
	"""

class ObjectDeleted(APIError):
	"""
	Object is marked as deleted, action may not be executed on it.
	"""

class NotAuthorized(APIError):
	"""
	User or admin is not authorized to perform this action.
	"""

class InvalidRequest(APIError):
	"""
	Request is invalid.
	"""

class NameTaken(APIError):
	"""
	User or board name is taken.
	"""

class NameInvalid(APIError):
	"""
	User or board name is not valid.
	"""

class PasswordInsecure(APIError):
	"""
	Password does not fulfill server requirements.
	"""

class AlreadyBlocked(APIError):
	"""
	You have already blocked this user.
	"""

class AlreadyFriends(APIError):
	"""
	You are already friends with this user.
	"""

class AlreadySent(APIError):
	"""
	You have already sent a friend request to this user.
	"""

class AlreadyAdded(APIError):
	"""
	User is already added to the board.
	"""

class NotFriends(APIError):
	"""
	You are not friends with this user.
	"""

def api_error(message: str, status_code: int, **data) -> APIError:
	"""
	Construct an APIError or one of its subclasses.
	"""
	return APIError(message, status_code, **data)

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
				raise api_error(errmsg, resp.status_code, **errdata)
			else:
				raise api_error(None, resp.status_code, text=resp.text)
		
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

class SubtextObj:
	"""
	An object that exists on a Subtext instance, represented by a UUID.
	"""
	def __init__(self, id: UUID, ctx: Optional[Context] = None):
		self.id = id
		self.ctx = ctx
	def refresh(self):
		"""
		Update this object with the latest data from the Subtext instance.
		"""
		raise NotImplementedError()
