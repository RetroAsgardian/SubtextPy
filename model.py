#!/usr/bin/env python3
"""
SubtextPy.model
"""
from enum import Enum
from uuid import UUID
from datetime import datetime

from typing import Optional, List

# Header

class SubtextObj: pass
class UserPresence(Enum): pass
class User: pass
class PublicKey: pass
class BoardEncryption(Enum): pass
class Board: pass
class Message: pass

# End Header

class SubtextObj:
	"""
	An object that exists on a Subtext instance, referenced by a UUID.
	"""
	def __init__(self, id: UUID, context=None):
		self.id: UUID = id
		self._context = context
	
	def refresh(self):
		"""
		Populates the object with new, updated values.
		"""
		raise NotImplementedError()

class UserPresence(Enum):
	offline = "Offline"
	online = "Online"
	away = "Away"
	busy = "Busy"

class User(SubtextObj):
	def __init__(self, id: UUID, context=None):
		super().__init__(id, context)
		
		self.name: Optional[str] = None
		
		self.presence: Optional[UserPresence] = None
		self.last_active: Optional[datetime] = None
		self.status: Optional[str] = None
		
		self.is_deleted: Optional[bool] = None
		
		self.blocked: Optional[List[User]] = None
		self.friends: Optional[List[User]] = None
		self.friend_requests: Optional[List[User]] = None
		self.keys: Optional[List[PublicKey]] = None

class PublicKey(SubtextObj):
	def __init__(self, id: UUID, context=None):
		super().__init__(id, context)
		
		self.owner: Optional[User] = None
		
		self.key_data: Optional[bytes] = None
		
		self.publish_time: Optional[datetime] = None

class BoardEncryption(Enum):
	none = "None"
	shared_key = "SharedKey"
	gnupg = "GnuPG"

class Board(SubtextObj):
	def __init__(self, id: UUID, context=None):
		super().__init__(id, context)
		
		self.name: Optional[str] = None
		
		self.is_direct: Optional[bool] = None
		
		self.last_update: Optional[datetime] = None
		self.last_significant_update: Optional[datetime] = None
		
		self.owner: Optional[User] = None
		
		self.encryption: Optional[BoardEncryption] = None
		
		self.messages: Optional[List[Message]] = None
		
		self.members: Optional[List[User]] = None

class Message(SubtextObj):
	def __init__(self, id: UUID, context=None):
		super().__init__(id, context)
		
		self.author: Optional[User] = None
		
		self.timestamp: Optional[datetime] = None
		
		self.type: Optional[str] = None
		self.content: Optional[bytes] = None
		self.is_system: Optional[bool] = None
