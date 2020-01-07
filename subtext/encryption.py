#!/usr/bin/env python3
"""
subtext.encryption
"""
import gnupg

from .user import User

from typing import Optional, List, Tuple

class Encryption:
	"""
	Provides encryption functionality for Subtext.
	"""
	def __init__(self, gpg_dir: Optional[str] = None):
		self.gpg = gnupg.GPG(use_agent=True, gnupghome=gpg_dir)
		self.gpg.encoding = 'utf-8'
	
	def get_user_key_uid(self, user: User) -> Tuple[str, str]:
		"""
		Return key "name" and "email" for the given user.
		"""
		if user.name is None:
			user.refresh()
		
		return (
			'{}@{}'.format(user.name, user.ctx.instance_name),
			'{}@{}'.format(user.id, user.ctx.instance_id)
		)
	
	def get_user_keys(self, user: User) -> List[str]:
		"""
		Get keys for the given user.
		"""
		name, email = self.get_user_key_uid(user)
	
	def gen_key(self,
		user: User,
		passphrase: Optional[str] = None,
		*,
		expire_years: int = 5
	) -> bytes:
		"""
		Generate a key for use with Subtext.
		"""
		name, email = self.get_user_key_uid(user)
		
		key = self.gpg.gen_key(self.gpg.gen_key_input(
			# RSA-2048 for signing and RSA-3072 for encryption
			# provides good security while reducing message size
			key_type='RSA',
			key_length=2048,
			key_usage='sign',
			subkey_type='RSA',
			subkey_length=3072,
			subkey_usage='encrypt',
			
			name_real=name,
			name_comment='Subtext',
			name_email=email,
			expire_date=(0 if expire_years <= 0 else "{}y".format(expire_years)),
			passphrase=passphrase
		))
		
		return self.gpg.export_keys([key.fingerprint], armor=False)
	
	def encrypt(self,
		data: bytes,
		recipients: List[User],
		sender: User,
		passphrase: Optional[str] = None,
		*,
		compress: bool = False
	) -> bytes:
		"""
		Encrypt and sign some data.
		"""
		crypt = self.gpg.encrypt(
			data,
			["{0}@{1}".format(user.id, user.ctx.instance_name) for user in recipients],
			sign="{0}@{1}".format(sender.id, sender.ctx.instance_name),
			passphrase=passphrase,
			always_trust=True,
			armor=False,
			extra_args=(['-z', '0'] if not compress else None)
		)
		return crypt.data
	
	def decrypt(self,
		data: bytes,
		passphrase: Optional[str] = None
	) -> Tuple[bytes, bool]:
		"""
		Decrypt and verify some data.
		"""
		crypt = self.gpg.decrypt(
			data,
			passphrase=passphrase,
			always_trust=True
		)
		return (crypt.data, crypt.trust_level is not None and crypt.trust_level >= crypt.TRUST_FULLY)
