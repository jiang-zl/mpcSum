from network.client import Client
import threading
from crypto.addictiveSecretShare import AddSecretShare


def job(c: Client, idx: int, ip_pool: list, sharing: AddSecretShare):
    c.send_shares(ip_pool, sharing)
    partial_sum = c.recv_shares(sharing)
    c.broadcast_sum(ip_pool, partial_sum)
    result = c.aggregate(sharing)
    print("result_{} = {}".format(idx, result))
    c.close_socket()


def multi_thread_proc(clients: list, count: int, ip_pool: list, sec_lvl: int):
    threads = []
    sharing = AddSecretShare(sec_lvl)
    for idx in range(count):
        cur_thread = threading.Thread(target=job, args=(clients[idx], idx, ip_pool, sharing))
        threads.append(cur_thread)
        cur_thread.start()
    for t in threads:
        t.join()
