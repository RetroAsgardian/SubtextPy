#!/usr/bin/env python3
"""
subtext.content
"""
import hashlib
import struct
from typing import Optional

class Content:
	"""
	Represents message content.
	"""
	def from_bytes(self, data: bytes):
		"""
		Convert from raw message bytes.
		"""
		raise NotImplementedError()
	def to_bytes(self) -> bytes:
		"""
		Convert to raw message bytes.
		"""
		raise NotImplementedError()

class FallbackContent(Content):
	"""
	If nothing else matches.
	"""
	def __init__(self, *, data: Optional[bytes] = None):
		self.data = data
	def from_bytes(self, data: bytes):
		self.data = data
	def to_bytes(self) -> bytes:
		return self.data

class TextContent(Content):
	"""
	Text encoded in UTF-8 format.
	"""
	def __init__(self, *, text: Optional[str] = None):
		self.text = text
	def from_bytes(self, data: bytes):
		self.text = data.decode('utf-8')
	def to_bytes(self) -> bytes:
		return self.text.encode('utf-8')

class FileContent(Content):
	"""
	Simple file container.
	"""
	def __init__(self, *, name: Optional[str] = None, type: Optional[str] = None, data: Optional[bytes] = None):
		self.name = name
		self.type = type
		self.data = data
	def to_bytes(self) -> bytes:
		header = bytearray()
		
		# Name
		header.extend(self.name.encode('utf-8'))
		header.extend(b'\x00')
		
		# Type
		header.extend(self.type.encode('utf-8'))
		header.extend(b'\x00')
		
		# Size
		header.extend(struct.pack('>i', len(self.data)))
		
		# Hash
		sha256 = hashlib.sha256()
		sha256.update(self.data)
		header.extend(sha256.digest())
		
		# Data offset, header, data
		return struct.pack('>i', len(header) + 4) + header + self.data
	def from_bytes(self, data: bytes):
		(data_offset,) = struct.unpack('>i', data[:4])
		print("data_offset: 0x{:08x}".format(data_offset))
		
		self.data = data[data_offset:]
		
		header = bytearray(data[4:data_offset])
		
		name_bytes = bytearray()
		while True:
			x = header.pop(0)
			if x == 0x00:
				break
			name_bytes.append(x)
		self.name = name_bytes.decode('utf-8')
		
		type_bytes = bytearray()
		while True:
			x = header.pop(0)
			if x == 0x00:
				break
			type_bytes.append(x)
		self.type = type_bytes.decode('utf-8')
		
		(size, ) = struct.unpack('>i', header[:4])
		if size != len(self.data):
			raise ValueError("Size mismatch")
		
		digest = bytes(header[4:])
		sha256 = hashlib.sha256()
		sha256.update(self.data)
		if sha256.digest() != digest:
			raise ValueError("Hash mismatch")
		
