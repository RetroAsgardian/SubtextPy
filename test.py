#!/usr/bin/env python3
import subtext

from uuid import UUID

client = subtext.Client("http://localhost:8000")

client.login('testing', 'password')

# TODO stuff

client.logout()