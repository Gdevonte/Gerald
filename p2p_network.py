import socket
import threading
import json

class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        threading.Thread(target=self.listen_for_peers).start()

    def listen_for_peers(self):
        while True:
            client, address = self.server.accept()
            threading.Thread(target=self.handle_peer, args=(client,)).start()

    def handle_peer(self, client):
        try:
            data = client.recv(1024)
            if data:
                message = json.loads(data.decode('utf-8'))
                # Process message (e.g., new transaction, new block, etc.)
        except Exception as e:
            print(f"Error handling peer: {e}")
        finally:
            client.close()

    def connect_to_peer(self, peer_host, peer_port):
        peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer.connect((peer_host, peer_port))
        self.peers.add((peer_host, peer_port))
        # Send some initial data if needed
