"""
Kafka localhost proxy (WORKAROUND).

Masalah: broker Kafka di 10.70.0.56 meng-advertise dirinya sebagai
localhost:9092/9095/9097 (advertised.listeners salah di sisi broker).
Akibatnya client remote connect ke bootstrap sukses, tapi saat fetch data
diarahkan ke "localhost" → ECONNREFUSED.

Workaround: jalankan proxy TCP lokal yang listen di localhost:PORT dan
forward ke 10.70.0.56:PORT. Dengan begitu "localhost:9092" yang di-advertise
broker benar-benar sampai ke broker asli.

Fix permanen tetap: tim broker set advertised.listeners=10.70.0.56:<port>.

Usage:
    python -m tools.kafka_localhost_proxy
Stop: Ctrl+C (atau kill prosesnya).
"""

import socket
import threading
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - kafka-proxy - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

REMOTE_HOST = "10.70.0.56"
# port lokal -> port remote (1:1 sesuai advertised.listeners broker)
PORT_MAP = {9092: 9092, 9095: 9095, 9097: 9097}


def _pipe(src: socket.socket, dst: socket.socket):
    """Salin byte dari src ke dst sampai salah satu tutup."""
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def _handle(client: socket.socket, remote_port: int):
    try:
        upstream = socket.create_connection((REMOTE_HOST, remote_port), timeout=10)
    except OSError as e:
        logger.error(f"Gagal connect ke {REMOTE_HOST}:{remote_port}: {e}")
        client.close()
        return
    threading.Thread(target=_pipe, args=(client, upstream), daemon=True).start()
    threading.Thread(target=_pipe, args=(upstream, client), daemon=True).start()


def _listener(local_port: int, remote_port: int):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("127.0.0.1", local_port))
    except OSError as e:
        logger.error(f"Tidak bisa bind 127.0.0.1:{local_port}: {e}")
        return
    srv.listen(128)
    logger.info(f"Proxy listen 127.0.0.1:{local_port} -> {REMOTE_HOST}:{remote_port}")
    while True:
        try:
            client, _ = srv.accept()
        except OSError:
            break
        _handle(client, remote_port)


def main():
    threads = []
    for local_port, remote_port in PORT_MAP.items():
        t = threading.Thread(target=_listener, args=(local_port, remote_port), daemon=True)
        t.start()
        threads.append(t)
    logger.info("Kafka localhost proxy aktif. Ctrl+C untuk stop.")
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        logger.info("Proxy dihentikan.")
        sys.exit(0)


if __name__ == "__main__":
    main()
