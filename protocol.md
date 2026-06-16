# Chatterbox Protocol - Version 1
## Data structure
- Messages are transmitted over the wire in a UTF-8 encoded TCP byte stream. This can be optionally encrypted using Transport Layer Security (TLS).
- The Chatterbox Protocol uses port 2428 TCP as the default port.
- If the server requires TLS, but the client attempts to connect without initiating a TLS handshake, the server must respond with error SEC1. 
- Messages are referred to as frames. All numbers are sent big-endian. A frame is made up of several parts:
  - **Part 1**: 1 byte, the Chatterbox protocol version number.
  - **Part 2**: 1 byte, a bool which acts as the error switch. When set to 1, the client must regard the chat message as the error message.
  - **Part 3:** 4 bytes, the **session key length** - "Y".
  - **Part 4:** 4 bytes, the **message length** - "Z".  
  - **Part 5:** Y bytes, the **session key**. 
  - **Part 6:** Z bytes, the **chat message**.
- A frame may contain a session key length of 0 and omit the session key if the error switch is set to 1.
- If the error switch is set to a value other than 0 or 1, the server must respond with ERR1.   
- If a message is malformed and does not conform with the above, the server must respond with ERR1.
- A session key must not exceed 300 bytes.
- If a session key is too long, a server must respond with error ERR2. 
- A chat message must not exceed 3000 bytes.
- If a chat message is too long, a server must respond with error ERR3.
- Timestamps are not conveyed in frames. The server and client may determine the timestamp based on the time that they received the message.
- If the server does not support the version of the Chatterbox protocol included in the frame, the server must respond with ERR4.

## Session Key
- The session key must be a JSON Web Token (JWT).
- JWTs must be signed with the HS256 algorithm. 
- The JWT must contain 2 claims
  - sub: to be treated as the username.
  - exp: the expiry time of the key. 
- If a JWT is invalid, the server must respond with error AUTH1.
- If the server is refusing to authenticate the user, it must respond with error AUTH2.
- If the server is not accepting the session key because it has expired, the server must respond with error AUTH3.

## Errors
Error messages must be sent within the chat message of a frame, exactly as follows.
- ERR1: Invalid frame
- ERR2: Session key too long
- ERR3: Chat message too long
- ERR4: Chatterbox protocol not supported
- AUTH1: Session key invalid
- AUTH2: Authentication failed
- AUTH3: Re-authentication required
- SEC1: TLS required

Only the server must send error messages.