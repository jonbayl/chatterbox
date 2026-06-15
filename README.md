# chatterbox
A very noddy chat server and client written in Python. 

This is largely a learning project to enhance my own understanding of:
- Network sockets
- Using the Python sockets library
- Async functions and asyncio

Also has relatively simple TLS encryption capabilities, with the client validation (not hardened by any stretch!). 

# TODO:
- [ x ] Convert server.py to async functions so it can actually handle more than one connected client properly... 
- [ ] Implement a simple chat protocol so that messages are always handled properly. Support passing metadata with messages.
- [ ] User creation and management?
- [ ] Server tools - e.g. global message broadcast and basic administration like ban/kick.