from network.client import Client
from network.task import *

if __name__ == '__main__':
    ip_pool = [
        ["Your Host IP", 21000],
        ["Your Host IP", 21001],
        ["Your Host IP", 21002],
        ["Your Host IP", 21003],
        ["Your Host IP", 21004],
    ]
    weights = [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15],
        [16, 17, 28, 19, 20],
        [21, 22, 23, 24, 25]
    ]
    # agg = [55, 60, 65, 70, 75]
    n_clients = len(ip_pool)
    clients = [0] * n_clients
    for idx in range(n_clients):
        clients[idx] = Client(idx, ip_pool[idx][0], ip_pool[idx][1], n_clients, weights[idx])
    multi_thread_proc(clients, n_clients, ip_pool, 128)
