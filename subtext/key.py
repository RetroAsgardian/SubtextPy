#!/usr/bin/env python3
"""
subtext.key
"""
from .common import Context, SubtextObj

from uuid import UUID
from datetime import datetime
import iso8601
import json

from typing import Optional

# HEADER
class Key(SubtextObj): pass

from .user import User

class Key(SubtextObj):
	def __init__(self, id: UUID, ctx: Optional[Context] = None, *,
		publish_time: Optional[datetime] = None,
		owner: Optional[User] = None
	):
		super().__init__(id, ctx)
		
		self.publish_time = publish_time
		self.owner = owner
		
		self.data = None
	def refresh(self):
		resp = self.ctx.get("/Subtext/key/{}".format(self.id))
		
		self.data = resp.content
		
		if 'X-Metadata' in resp.headers:
			metadata = json.loads(resp.headers['X-Metadata'])
			
			self.publish_time = iso8601.parse_date(metadata['publishTime'])
			
			if self.owner is None or self.owner.id != UUID(metadata['ownerId']):
				self.owner = User(UUID(metadata['ownerId']))
