import sys
import time
import socket

def wait_for_psql(host, port, timeout=60):
    start = time.time()
    while True:
        try:
            with socket.create_connection((host, int(port)), timeout=2):
                print(f"PostgreSQL is available at {host}:{port}")
                return
        except Exception:
            if time.time() - start > timeout:
                print(f"Timeout waiting for PostgreSQL at {host}:{port}")
                sys.exit(1)
            time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: wait-for-psql.py host port")
        sys.exit(1)
    wait_for_psql(sys.argv[1], sys.argv[2])
