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
	
	print("Logged in as {}@{} ({}@{})".format(user.name, client.instance_name, user.id, client.instance_id))
	
	crypt = subtext.Encryption(user)
	
	if len(crypt.get_user_keys(user)) < 1:
		print("Generating key...")
		fp = crypt.gen_key(user)
	else:
		fp = crypt.get_user_keys(user)[0]
	
	print("Key FP: {}".format(fp))
	
	print()
	
	print("Boards:")
	for board in client.get_boards():
		print("- #{} ({})".format(board.name, board.id))
	
	board = client.get_board(UUID(input('Enter a board ID: ')))
	
	print()
	
	print("Members of #{}:".format(board.name))
	for member in board.members:
		member.refresh()
		print("- @{} ({})".format(member.name, member.id))
	
	print()
	
	print("Messages in #{}:".format(board.name))
	for msg in board.get_messages():
		print("[{}] @{}, {}:".format(msg.type, msg.author.id, msg.timestamp))
		if msg.content is None:
			msg.refresh()
		
		i = 0
		for i in range(0, len(msg.content), 16):
			chunk = msg.content[i:i+16]
			print("0x{:08x}\t".format(i), end="")
			for byte in chunk:
				print("{:02x}".format(byte), end=" ")
			print(("\x1b[90m..\x1b[0m " * (16 - len(chunk))) + "\t", end="")
			for byte in chunk:
				if byte >= 0x20 and byte <= 0x7e:
					print(chr(byte), end="")
				else:
					print("\x1b[90m.\x1b[0m", end="")
			print("\x1b[90m.\x1b[0m" * (16 - len(chunk)))
		print()
	
	client.logout()

if __name__ == "__main__":
	main()
