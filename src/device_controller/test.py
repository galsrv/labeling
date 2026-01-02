import socket

from devices.printers.dpl.send_label import build_dpl_unicode_label  # noqa: F401
from devices.printers.dpl.upload_font import build_dpl_ttf_upload_commands  # noqa: F401
from devices.printers.dpl.upload_image import build_dpl_image_upload_commands  # noqa: F401

IP = '192.168.90.36'
PORT = 9100
TIMEOUT = 3.0

# COMMAND = b'''\x02ySCP\x0D'''

# COMMAND = b'''\x02KC\x0D'''

# COMMAND = b'''\x02W*\x0D'''

data = (
    "<STX>yUUC<CR>"
    "<STX>L<CR>"
    "4911u6601000100P015P009Тестовый текст шрифтом Oswald: абвгдеёжзикл...уфцчщьъэюя123()_\"\"<CR>"
    "4911u7701000200P015P009Тестовый EAN13:<CR>"
    "4F00" + "070" + "01000350" + "012345678901<CR>"
    "4911u7705000200P015P009Тестовый GS1 DataMatrix:<CR>"
    "4W1c00" + "000" + "05000400" + "2000" + "000000" + "<FNC1>" + "0104603934000793215?ZjQDTZ4NBNy<GS>93zFAP<CR>"
    "4911u5501000500P015P009Тестовая картинка:<CR>"
    "1Y00" + "000" + "05000500" + "vilka<CR>"
    "E<CR>"
)

COMMAND = build_dpl_unicode_label(data)

# COMMAND = build_dpl_ttf_upload_commands('devices/printers/fonts/roboto.ttf', '77')
# COMMAND = build_dpl_ttf_upload_commands('devices/printers/fonts/oswald.ttf', '66')
# COMMAND = build_dpl_ttf_upload_commands('devices/printers/fonts/opensans.ttf', '55')

# COMMAND = build_dpl_image_upload_commands("devices/printers/images/eac.jpg", image_name="eac")


def test_device_connection(ip: str, port: int, timeout: float) -> str:
    """Connects to any device with expanded diagnostics.

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
        #for command in COMMANDS:
        try:
            print(f"[*] Sending command: {COMMAND[:30]}...{COMMAND[-10:]}")
            sock.sendall(COMMAND)
            print("[+] Command sent successfully.")
        except socket.timeout:
            return "[ERROR] Timeout while sending data."
        except OSError as e:
            return f"[ERROR] Failed to send command: {e}"

        # ---- RECEIVE RESPONSE ----
        # for _ in range(10):
        #     data = sock.recv(4096)
        #     print(data)
        # sock.close()

        try:
            print("[*] Waiting for response...")
            data = sock.recv(4096)
            if not data:
                return "[ERROR] Remote device closed connection without sending data."

            return f"[+] Received raw response: {data!r}"
        except socket.timeout:
            return "[ERROR] Read timeout — connected, but device sent NO DATA."
        except OSError as e:
            return f"[ERROR] Failed while reading from socket: {e}"
        finally:
            sock.close()
            print("[*] Socket closed.")

    except Exception as general_error:
        return f"[UNEXPECTED ERROR] {general_error}"


if __name__ == "__main__":
    result = test_device_connection(IP, PORT, TIMEOUT)
    print("\n=== RESULT ===")
    print(result)
