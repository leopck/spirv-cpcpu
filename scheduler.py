import argparse
import copy
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


def read_bin(conn):
    bin = b""
    while True:
        data = conn.recv(4096)
        if not data:
            break
        bin += data
    return bin


def build_graph(bin):
    instructions = bin.decode('utf-8').splitlines()
    graph = {'ids': {}, 'smap': {}, 'instructions': {}, 'ready': set(), 'complete': set()}
    fadd = ("FADD", lambda x, y: x + y)
    for instruction in instructions:
        words = instruction.split()
        if words[0] == 'FADD' and len(words) == 4:
            # depend on order for now
            dst = int(words[1].split('=')[1])
            src1 = int(words[2].split('=')[1])
            src2 = int(words[3].split('=')[1])
            if graph['instructions'].get(dst):
                # duplicate dst not allowed yet
                return
            graph['ids'][dst] = ""
            graph['ids'][src1] = ""
            graph['ids'][src2] = ""
            if dsts := graph['smap'].get(src1):
                dsts.add(dst)
            else:
                graph['smap'][src1] = set([dst])
            if dsts := graph['smap'].get(src2):
                dsts.add(dst)
            else:
                graph['smap'][src2] = set([dst])
            graph['instructions'][dst] = {'func': fadd, 'srcs': [src1, src2]}
    if len(graph) == 4:
        return
    return graph


def update_ready(graph, id_number):
    if not graph['smap'].get(id_number):
        return
    for dst in graph['smap'][id_number]:
        ready = True
        for sid in graph['instructions'][dst]['srcs']:
            if not graph['ids'][sid]:
                ready = False
        if ready:
            graph['ready'].add(dst)


def parse_data(graph, data, rest):
    blob = rest + data.decode('utf-8')
    lines = blob.splitlines()
    llen = len(lines)
    for idx in range(llen):
        # line format is id=val; -> '6=3.315;'
        line = lines[idx]
        if line[-1] != ";":
            # incomplete line, ensure there isn't trailing line data though
            if idx == llen - 1:
                return graph, line
            # incomplete line but more lines -> error
            return None, ""
        idn, val = line[:-1].split('=')
        idn = int(idn)
        if graph['ids'].get(idn) != "":
            # id isn't in the graph or id sent multiple times -> error
            return None, ""
        # need to do real type handling in bin still
        # for now all vals are floats
        graph['ids'][idn] = float(val)
        update_ready(graph, idn)
    return graph, ""


def eval_graph(graph):
    while len(graph['ready']) > 0:
        new_ready = set()
        for idn in graph['ready']:
            node = graph['instructions'][idn]
            srcs = [graph['ids'][src] for src in node['srcs']]
            graph['ids'][idn] = node['func'][1](*srcs)
            print(f"computed {node['func'][0]} {srcs} -> {graph['ids'][idn]}")
            graph['complete'].add(idn)
            new_ready.add(idn)
        for idn in new_ready:
            update_ready(graph, idn)
        graph['ready'].difference_update(graph['complete'])
    if len(graph['complete']) == len(graph['instructions']):
        return 0
    return 1


def process_data(tcp_socket, base_graph):
    rest = ""
    while True:
        conn, client = tcp_socket.accept()
        graph = copy.deepcopy(base_graph)
        while True:
            data = conn.recv(4096)
            if not data:
                print("incomplete data from client, resetting")
                break
            graph, rest = parse_data(graph, data, rest)
            if not graph and not rest:
                print("bad data from client, resetting")
                break
            result = eval_graph(graph)
            if result == 0:
                print("completed kernel, exiting")
                return


def server_host(ip, port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((ip, port))
    tcp_socket.listen(1)

    while True:
        conn, client = tcp_socket.accept()
        bin = read_bin(conn)
        if bin:
            graph = build_graph(bin)
            if graph:
                # we have our marching orders, now we need data
                break
    process_data(tcp_socket, graph)


def main():
    args = parse_args()
    if args.client:
        client_connect(args.ip, args.port, args.client)
    else:
        server_host(args.ip, args.port)


if __name__ == '__main__':
    main()
