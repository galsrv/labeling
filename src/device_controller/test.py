import socket


def test_mt_sics_diagnostic(ip: str, port: int, timeout: float = 3.0) -> str:
    """Connects to MT-SICS scale with expanded diagnostics.

    Returns detailed diagnostic message.
    """
    try:
        print(f"[*] Attempting connection to {ip}:{port} (timeout={timeout}s)")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        # ---- CONNECT ----
        try:
            sock.connect((ip, port))
            print("[+] TCP connection established.")
        except socket.timeout:
            return "[ERROR] Connection attempt timed out — host or port unreachable."
        except ConnectionRefusedError:
            return "[ERROR] Connection refused — device reachable but port is closed."
        except OSError as e:
            return f"[ERROR] OS-level connection error: {e}"

        # ---- SEND COMMAND ----
        try:
            cmd = b"0x05\r\n"
            print(f"[*] Sending command: {cmd!r}")
            sock.sendall(cmd)
            print("[+] Command sent successfully.")
        except socket.timeout:
            return "[ERROR] Timeout while sending data."
        except OSError as e:
            return f"[ERROR] Failed to send command: {e}"

        # ---- RECEIVE RESPONSE ----
        try:
            print("[*] Waiting for response...")
            data = sock.recv(4096)
        except socket.timeout:
            return "[ERROR] Read timeout — connected, but scale sent NO DATA."
        except OSError as e:
            return f"[ERROR] Failed while reading from socket: {e}"
        finally:
            sock.close()
            print("[*] Socket closed.")

        if not data:
            return "[ERROR] Remote device closed connection without sending data."

        return f"[+] Received raw response: {data!r}"

    except Exception as general_error:
        return f"[UNEXPECTED ERROR] {general_error}"


if __name__ == "__main__":
    ip = "192.168.238.51"
    port = 4004

    result = test_mt_sics_diagnostic(ip, port)
    print("\n=== RESULT ===")
    print(result)
