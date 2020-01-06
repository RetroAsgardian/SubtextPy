#!/usr/bin/env python3
"""
subtext.board
"""
from .common import Context, SubtextObj

from .user import User

from uuid import UUID
from datetime import datetime
import iso8601

from enum import Enum
from typing import Optional

class BoardEncryption(Enum):
	gnupg = "GnuPG"
	shared_key = "SharedKey"
	none = "None"

class Board(SubtextObj):
	def __init__(self, id: UUID, ctx: Optional[Context] = None, *, name: Optional[str] = None, owner: Optional[User] = None, encryption: Optional[BoardEncryption] = None, last_update: Optional[datetime] = None, last_significant_update: Optional[datetime] = None):
		super().__init__(id, ctx)
		
		self.name = name
		self.owner = owner
		self.encryption = encryption
		
		self.last_update = last_update
		self.last_significant_update = last_significant_update
	def refresh(self):
		resp = self.ctx.get("/Subtext/board/{}".format(self.id), params={
			'sessionId': self.ctx.session_id()
		}).json()
		
		self.name = resp.get('name', None)
		self.owner = User(UUID(resp['ownerId']), self.ctx) if resp.get('ownerId', None) else None
		self.encryption = BoardEncryption(resp['encryption']) if resp.get('encryption', None) else None
		
		self.last_update = iso8601.parse_date(resp['lastUpdate']) if resp.get('lastUpdate', None) else None
		self.last_significant_update = iso8601.parse_date(resp['lastSignificantUpdate']) if resp.get('lastSignificantUpdate', None) else None
	
