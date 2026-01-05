import socket
import threading

HOST = "127.0.0.1"
PORT = 12345


def recv_loop(sock: socket.socket) -> None:
    # Receive messages from server while user types commands
    buffer = ""

    while True:
        try:
            data = sock.recv(4096)
        except Exception:
            print("[CLIENT] Connection error.")
            break

        if not data:
            print("[CLIENT] Server closed connection.")
            break

        # TCP is stream-based, so we split messages by newline
        buffer += data.decode("utf-8", errors="replace")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if line:
                print(f"[RECV] {line}")


def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print(f"[CLIENT] Connected to {HOST}:{PORT}")

    # Thread for receiving server messages
    threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()

    while True:
        try:
            cmd = input().strip()
        except (EOFError, KeyboardInterrupt):
            cmd = "DISCONNECT"

        if not cmd:
            continue

        try:
            # Newline marks end of command
            sock.sendall((cmd + "\n").encode("utf-8"))
        except Exception:
            print("[CLIENT] Send failed.")
            break

        if cmd.upper() == "DISCONNECT":
            break

    try:
        sock.close()
    except Exception:
        pass

    print("[CLIENT] Closed.")


if __name__ == "__main__":
    main()
