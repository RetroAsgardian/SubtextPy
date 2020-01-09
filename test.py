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
		print("({}) @{}, {}:".format(msg.type, msg.author.id, msg.timestamp))
		if msg.content is None:
			msg.refresh()
		
		i = 0
		print("\t", end="")
		for byte in msg.content:
			print("{:x}".format(byte), end="\n\t" if i % 16 == 0 else " ")
			i += 1
		print()
	
	client.logout()

if __name__ == "__main__":
	main()
