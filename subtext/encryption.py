#!/usr/bin/env python3
"""
subtext.encryption
"""
import gnupg

from .user import User

from typing import Optional, List

class Encryption:
	def __init__(self):
		self.gpg = gnupg.GPG(use_agent=True)
		self.gpg.encoding = 'utf-8'
	def gen_key(self,
		user: User,
		passphrase: Optional[str] = None,
		*,
		never_expire: bool = False
	) -> bytes:
		if user.name is None:
			user.refresh()
		
		key = self.gpg.gen_key(self.gpg.gen_key_input(
			key_type='RSA',
			key_length=3072,
			key_usage='sign',
			subkey_type='RSA',
			subkey_length=3072,
			subkey_usage='encrypt',
			name_real=user.name,
			name_comment='',
			name_email='{0}@{1}'.format(user.id, user.ctx.instance_name),
			expire_date=(0 if never_expire else "5y"),
			passphrase=passphrase
		))
		
		return self.gpg.export_keys([key.fingerprint], armor=False)
	def encrypt(self,
		data: bytes,
		recipients: List[User],
		sender: User,
		passphrase: Optional[str] = None
	) -> bytes:
		crypt = self.gpg.encrypt(
			data,
			["{0}@{1}".format(user.id, user.ctx.instance_name) for user in recipients],
			sign="{0}@{1}".format(sender.id, sender.ctx.instance_name),
			passphrase=passphrase,
			always_trust=True,
			armor=False
		)
		return crypt.data
	def decrypt(self,
		data: bytes,
		passphrase: Optional[str] = None
	) -> bytes:
		crypt = self.gpg.decrypt(
			data,
			passphrase=passphrase,
			always_trust=True
		)
		return crypt.data
