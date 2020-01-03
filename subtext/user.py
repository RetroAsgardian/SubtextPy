#!/usr/bin/env python3
"""
subtext.user
"""
from .common import APIError, ContextError, Context, SubtextObj

from .key import Key

from uuid import UUID
from datetime import datetime
import iso8601

from enum import Enum
from typing import Optional, Union

class UserPresence(Enum):
	online = "Online"
	away = "Away"
	busy = "Busy"
	offline = "Offline"

class User(SubtextObj):
	def __init__(self, id: UUID, ctx: Optional[Context] = None):
		super().__init__(id, ctx)
		
		self.name = None
		
		self.presence = None
		self.last_active = None
		self.status = None
		
		self.is_deleted = None
		
		self.friends = None
		self.blocked = None
		self.friend_requests = None
		self.keys = None
	def refresh(self):
		resp = self.ctx.get("/Subtext/user/{}".format(self.id), params={
			'sessionId': self.ctx.session_id()
		}).json()
		
		self.name = resp.get('name', None)
		
		self.presence = UserPresence(resp['presence']) if resp.get('presence', None) else None
		self.last_active = iso8601.parse_date(resp['lastActive']) if resp.get('lastActive', None) else None
		self.status = resp.get('status', None)
		
		self.is_deleted = resp.get('isDeleted', None)
		
		self.friends = None
		self.blocked = None
		self.friend_requests = None
		
		if self.id == self.ctx.user_id():
			# Get friend list
			id_list = []
			start = 0
			while True:
				resp = self.ctx.get("/Subtext/user/{}/friends".format(self.id), params={
					'sessionId': self.ctx.session_id(),
					'start': start
				}).json()
				start += len(resp)
				if len(resp) <= 0:
					break
				for user_id in resp:
					if user_id not in id_list:
						friend_ids.append(user_id)
			self.friends = [User(user_id, self.ctx) for user_id in id_list]
			
			# Get block list
			id_list = []
			start = 0
			while True:
				resp = self.ctx.get("/Subtext/user/{}/blocked".format(self.id), params={
					'sessionId': self.ctx.session_id(),
					'start': start
				}).json()
				start += len(resp)
				if len(resp) <= 0:
					break
				for user_id in resp:
					if user_id not in id_list:
						id_list.append(user_id)
			self.blocked = [User(user_id, self.ctx) for user_id in id_list]
			
			# Get friend request list
			id_list = []
			start = 0
			while True:
				resp = self.ctx.get("/Subtext/user/{}/friendrequests".format(self.id), params={
					'sessionId': self.ctx.session_id(),
					'start': start
				}).json()
				start += len(resp)
				if len(resp) <= 0:
					break
				for user_id in resp:
					if user_id not in id_list:
						id_list.append(user_id)
			self.friend_requests = [User(user_id, self.ctx) for user_id in id_list]
		
		# Get public key list
		self.keys = []
		start = 0
		while True:
			resp = self.ctx.get("/Subtext/user/{}/keys".format(self.id), params={
				'sessionId': self.ctx.session_id(),
				'start': start
			}).json()
			start += len(resp)
			if len(resp) <= 0:
				break
			for key in resp:
				if not any(x for x in self.keys if x.id == key['id']):
					self.keys.append(Key(UUID(key['id']), self.ctx, publish_time=iso8601.parse_date(key['publishTime'])))
	
	def unfriend(self):
		"""
		Unfriend this user.
		"""
		self.ctx.delete("/Subtext/user/{}/friends/{}".format(self.ctx.user_id(), self.id), params={
			'sessionId': self.ctx.session_id()
		})
	
	def block(self):
		"""
		Block this user.
		"""
		self.ctx.post("/Subtext/user/{}/blocked".format(self.ctx.user_id()), params={
			'sessionId': self.ctx.session_id(),
			'blockedId': self.id
		})
	
	def unblock(self):
		"""
		Unblock this user.
		"""
		self.ctx.delete("/Subtext/user/{}/blocked/{}".format(self.ctx.user_id(), self.id), params={
			'sessionId': self.ctx.session_id()
		})
	
	def send_friend_request(self):
		"""
		Send a friend request to this user.
		"""
		self.ctx.post("/Subtext/user/{}/friendrequests".format(self.id), params={
			'sessionId': self.ctx.session_id()
		})
	
	def accept_friend_request(self):
		"""
		Accept this user's friend request.
		"""
		self.ctx.post("/Subtext/user/{}/friendrequests/{}".format(self.ctx.user_id(), self.id), params={
			'sessionId': self.ctx.session_id()
		})
	
	def reject_friend_request(self):
		"""
		Reject this user's friend request.
		"""
		self.ctx.delete("/Subtext/user/{}/friendrequests/{}".format(self.ctx.user_id(), self.id), params={
			'sessionId': self.ctx.session_id()
		})
	
	def add_key(self, data: bytes):
		"""
		Add a key to this user. (This must be the logged in user.)
		"""
		self.ctx.post("/Subtext/user/{}/keys".format(self.id), params={
			'sessionId': self.ctx.session_id()
		}, data=data)
	
	def set_presence(self, presence: UserPresence, until_time: Optional[datetime] = None, other_data: Optional[str] = None):
		"""
		Set this user's presence. (This must be the logged in user.)
		"""
		self.ctx.put("/Subtext/user/{}/presence".format(self.id), params={
			'sessionId': self.ctx.session_id(),
			'presence': presence,
			'untilTime': until_time,
			'otherData': other_data
		})
