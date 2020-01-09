#!/usr/bin/env python3
"""
test script for subtextpy
"""
import subtext

from uuid import UUID

def main():
	client = subtext.Client("http://localhost:5000")
	
	client.login('testing', 'password')
	user = client.get_user()
	
	print("Logged in as {}@{}".format(user.name, client.instance_name))
	
	crypt = subtext.Encryption(user)
	
	if len(crypt.get_user_keys(user)) < 1:
		print("Generating key...")
		fp = crypt.gen_key(user)
	else:
		fp = crypt.get_user_keys(user)[0]
	
	print("Key fingerprint: {}".format(fp))
	print()
	print("Key info:")
	print(repr(crypt.get_key_info(fp)))
	
	client.logout()

if __name__ == "__main__":
	main()
