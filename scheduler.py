import argparse
import socket

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument('ip')
    parser.add_argument('port', type=int)
    return parser.parse_args()


def client_connect(ip, port, infile):
    tcp_socket = socket.create_connection((ip, port))
    data = str.encode(infile.read())
    tcp_socket.sendall(data)
    tcp_socket.close()


def server_host(ip, port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((ip, port))
    tcp_socket.listen(1)

    while True:
        conn, client = tcp_socket.accept()
        sndfile = b""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            sndfile += data
        if sndfile:
            # do stuff with the bin
            pass


def main():
    args = parse_args()
    if args.client:
        client_connect(args.ip, args.port, args.client)
    else:
        server_host(args.ip, args.port)


if __name__ == '__main__':
    main()
