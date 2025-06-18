import argparse
import graphlib
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


def process_bin(bin):
    data = bin.decode('utf-8')
    try:
        instructions, text = data.split(':::')
    except:
        return
    funcs = {}
    flow = graphlib.TopologicalSorter()
    for instruction in instructions:
        words = instruction.split()
        if words[0] == 'FADD' and len(words) == 4:
            dst = words[1].split('=')[1]
            src1 = words[2].split('=')[1]
            src2 = words[3].split('=')[1]
            flow.add(dst, src1, src2)
            func = lambda x, y: x + y
            if dfunc := funcs.get(dst):
                dfunc.insert(0, func)
            else:
                funcs[dst] = [func]
        else:
            return
    flow.prepare()
    dp = 0
    while flow.is_active():
        for node in flow.get_ready():
            # process
            pass


def server_host(ip, port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((ip, port))
    tcp_socket.listen(1)

    while True:
        conn, client = tcp_socket.accept()
        bin = b""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            bin += data
        if bin:
            process_bin(bin)


def main():
    args = parse_args()
    if args.client:
        client_connect(args.ip, args.port, args.client)
    else:
        server_host(args.ip, args.port)


if __name__ == '__main__':
    main()
