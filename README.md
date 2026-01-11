# tcp chat project

TCP/IP chat application - Computer Networks project

This project implements a simple TCP-based chat application as part of the

Computer Networks course final project.

The system includes a central server and multiple clients that can communicate

with each other in real time using sockets.


---



Project Overview:

- Communication is based on the TCP protocol.
- A server listens for incoming client connections.
- Each client registers with a unique username.
- Clients can request to open a chat with another client by username.
- The server acts as a mediator and forwards messages between connected clients.
- The system supports multiple clients simultaneously using threads.
- The interface is text-based.

---


Files:

- `server.py` - TCP chat server (Part 2).
- `client.py` - TCP chat client (Part 2).
- `README.md` - Project description and instructions.

- `part1/` - Files for Part 1 (Encapsulation & Wireshark):
  - `group07_chat_input.csv` - Chat messages at the application layer.
  - `tcp_ip_encapsulation.ipynb` - Jupyter notebook that simulates TCP/IP encapsulation and sends packets for capture.

- `report/final_report.pdf` - Final project report (PDF).

---



Available Commands:

After starting a client, the following commands are supported:

-REGISTER <username>

Registers the client with a unique username.

-CONNECT <username>

Requests to open a chat with another registered client.

-MSG <message>

Sends a message to the connected client.

-DISCONNECT

Disconnects from the current chat.

-PING

Checks server availability.

-WHO

Displays a list of registered users (for testing).



---
How to run the project:

1. Make sure Python 3 is installed.
2. Open a terminal in the project folder.
3. Run the server:
   python server.py

4. Open another terminal and run a client:
   python client.py

5. In the client window type:
   REGISTER Noy

6. Open another client and type:
   REGISTER Elias

7. From Noy type:
   CONNECT Elias

8. Now both clients can send messages using:
   MSG hello

---

Example Usage:

Client 1:

REGISTER Noy

CONNECT Elias

MSG Hello!

Client 2:

REGISTER Elias

