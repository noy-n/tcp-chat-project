import socket
import threading

HOST = "127.0.0.1"
PORT = 12345

clients = {}  # name -> socket + connection state
clients_lock = threading.Lock()


def send_line(conn: socket.socket, text: str) -> None:
    try:
        conn.sendall((text + "\n").encode("utf-8"))
    except Exception:
        pass


def get_name_by_socket(conn: socket.socket):
    with clients_lock:
        for name, info in clients.items():
            if info["socket"] == conn:
                return name
    return None


def disconnect_pair_if_needed(name: str) -> None:
    with clients_lock:
        if name not in clients:
            return

        peer = clients[name]["connected_to"]
        clients[name]["connected_to"] = None

        if peer and peer in clients:
            clients[peer]["connected_to"] = None
            peer_conn = clients[peer]["socket"]
        else:
            peer_conn = None

    if peer_conn:
        send_line(peer_conn, "PEER_DISCONNECTED")


def remove_client(name: str) -> None:
    with clients_lock:
        info = clients.get(name)
        if not info:
            return

        try:
            info["socket"].close()
        except Exception:
            pass

        del clients[name]


def handle_client(conn: socket.socket, addr):
    print(f"[NEW CONNECTION] {addr}")
    send_line(conn, "WELCOME")

    buffer = ""

    while True:
        try:
            data = conn.recv(4096)
        except Exception:
            name = get_name_by_socket(conn)
            if name:
                disconnect_pair_if_needed(name)
                remove_client(name)
            break

        if not data:
            name = get_name_by_socket(conn)
            if name:
                disconnect_pair_if_needed(name)
                remove_client(name)
            break

        buffer += data.decode("utf-8", errors="replace")

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue

            if line.upper().startswith("REGISTER "):
                name = line.split(" ", 1)[1].strip()

                if not name:
                    send_line(conn, "ERROR INVALID_NAME")
                    continue

                if get_name_by_socket(conn):
                    send_line(conn, "ERROR ALREADY_REGISTERED")
                    continue

                with clients_lock:
                    if name in clients:
                        send_line(conn, "ERROR NAME_TAKEN")
                        continue
                    clients[name] = {"socket": conn, "connected_to": None}

                send_line(conn, f"REGISTER_OK {name}")
                continue

            if line.upper() == "PING":
                send_line(conn, "PONG")
                continue

            if line.upper().startswith("CONNECT "):
                target = line.split(" ", 1)[1].strip()
                sender = get_name_by_socket(conn)

                if not sender:
                    send_line(conn, "ERROR NOT_REGISTERED")
                    continue

                with clients_lock:
                    if target not in clients:
                        send_line(conn, "ERROR USER_NOT_FOUND")
                        continue

                    if clients[sender]["connected_to"] or clients[target]["connected_to"]:
                        send_line(conn, "ERROR USER_BUSY")
                        continue

                    clients[sender]["connected_to"] = target
                    clients[target]["connected_to"] = sender
                    target_conn = clients[target]["socket"]

                send_line(conn, f"CONNECT_OK {target}")
                send_line(target_conn, f"INCOMING_CONNECTION {sender}")
                continue

            if line.upper().startswith("MSG "):
                msg = line.split(" ", 1)[1]
                sender = get_name_by_socket(conn)

                if not sender:
                    send_line(conn, "ERROR NOT_REGISTERED")
                    continue

                with clients_lock:
                    peer = clients[sender]["connected_to"]
                    if not peer:
                        send_line(conn, "ERROR NOT_CONNECTED")
                        continue
                    peer_conn = clients[peer]["socket"]

                send_line(peer_conn, f"FROM {sender}: {msg}")
                send_line(conn, "MSG_SENT")
                continue

            if line.upper() == "DISCONNECT":
                sender = get_name_by_socket(conn)
                if sender:
                    disconnect_pair_if_needed(sender)
                    send_line(conn, "DISCONNECT_OK")
                continue

            if line.upper() == "WHO":
                with clients_lock:
                    names = ",".join(clients.keys())
                send_line(conn, f"USERS {names}")
                continue

            send_line(conn, "ERROR UNKNOWN_COMMAND")


def main() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
