#!/usr/bin/env python3
"""
subtext.encryption
"""
import gnupg

from .user import User

from typing import Optional, List, Tuple, Union

class Encryption:
	"""
	Provides encryption functionality for Subtext.
	"""
	def __init__(self, my_key: Optional[Union[User, str]] = None, *, gpg_dir: Optional[str] = None):
		self.gpg = gnupg.GPG(use_agent=True, gnupghome=gpg_dir)
		self.gpg.encoding = 'utf-8'
		
		self.my_key = None
		if my_key is not None:
			self.change_my_key(my_key)
	
	def change_my_key(self, my_key: Union[User, str]):
		"""
		Change the key used for signing and decryption.
		If a User is given, GnuPG will automatically select the best key for that user.
		"""
		if isinstance(my_key, User):
			self.my_key = self.get_user_key_uid(my_key)[1]
		else:
			self.my_key = my_key
	
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
		Get a list of key fingerprints for the given user, sorted with most recent key first.
		"""
		name, email = self.get_user_key_uid(user)
		keys = self.gpg.list_keys(keys=[name, email])
		
		keys.sort(key=(lambda key: -int(key['date'])))
		
		return [key['fingerprint'] for key in keys]
	
	def gen_key(self,
		user: User,
		passphrase: Optional[str] = None,
		*,
		expire_years: int = 5
	) -> str:
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
		
		return key.fingerprint
	
	def encrypt(self,
		data: bytes,
		recipients: List[Union[User, str]],
		passphrase: Optional[str] = None,
		*,
		compress: bool = False
	) -> bytes:
		"""
		Encrypt and sign some data.
		"""
		recipient_keys = []
		for x in recipients:
			if isinstance(x, User):
				recipient_keys.append(self.get_user_key_uid(x)[1])
			else:
				recipient_keys.append(x)
		
		crypt = self.gpg.encrypt(
			data,
			recipient_keys,
			sign=self.my_key,
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
