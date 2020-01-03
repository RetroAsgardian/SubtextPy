#!/usr/bin/env python3
"""
subtext.key
"""
from .common import APIError, ContextError, Context, SubtextObj

from uuid import UUID
from datetime import datetime
import iso8601

from typing import Optional, Union

class Key(SubtextObj):
	def __init__(self, id: UUID, ctx: Optional[Context] = None, *, publish_time: Optional[datetime] = None):
		super().__init__(id, ctx)
		
		self.publish_time = publish_time
		
		self.data = None
	def refresh(self):
		resp = self.ctx.get("/Subtext/key/{}".format(self.id))
		
		self.data = resp.content
