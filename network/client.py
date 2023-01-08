from crypto.addictiveSecretShare import AddSecretShare
import socket


class Client:
    def __init__(self, client_idx: int, ip_addr: str, ip_port: int, count: int, weight: list):
        self.client_idx = client_idx
        self.ip_addr = ip_addr
        self.ip_port = ip_port
        self.count = count
        self.weight = weight
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip_addr, self.ip_port))
        self.socket.setblocking(False)

    def get_shares(self, sharing: AddSecretShare) -> list:
        w_len = len(self.weight)
        ret = [[0] * self.count for _ in range(w_len)]
        for w_idx in range(w_len):
            cur_share = sharing.sharing(self.weight[w_idx], self.count)
            for sh_idx in range(self.count):
                ret[w_idx][sh_idx] = cur_share[sh_idx]
        return ret

    @staticmethod
    def agg_shares(sharing: AddSecretShare, ret: list, recv_msg: str, w_len: int):
        recv_num = recv_msg.split(' ')
        for w_idx in range(w_len):
            cur_num = int(recv_num[w_idx])
            ret[w_idx] = (ret[w_idx] + cur_num) % sharing.mod_q

    def send_shares(self, ip_pool: list, sharing: AddSecretShare):
        if len(ip_pool) != self.count:
            raise Exception("Number of parties is too less.")
        shares = self.get_shares(sharing)
        w_len = len(self.weight)
        for sh_idx in range(self.count):
            cur_msg = []
            for w_idx in range(w_len):
                cur_msg.append(shares[w_idx][sh_idx])
            send_info = " ".join(str(val) for val in cur_msg).encode('utf-8')
            dest_addr = (ip_pool[sh_idx][0], ip_pool[sh_idx][1])
            self.socket.sendto(send_info, dest_addr)
            print("Client {}:{} sends shares {} to client {}:{}".format(
                self.ip_addr, self.ip_port, send_info, dest_addr[0], dest_addr[1]
            ))

    def recv_shares(self, sharing: AddSecretShare) -> list:
        w_len = len(self.weight)
        ret, cnt = [0] * w_len, 0
        while True:
            try:
                self.socket.settimeout(30)
                recv_msg, recv_ip = self.socket.recvfrom(4096)
                recv_msg = recv_msg.decode('utf-8')
                print("Client {}:{} receives shares {} from client {}".format(
                    self.ip_addr, self.ip_port, recv_msg, recv_ip
                ))
                Client.agg_shares(sharing, ret, recv_msg, w_len)
            except socket.timeout:
                if cnt >= self.count:
                    print("Receive task is finished.")
                else:
                    print("Receive data timeout, break...")
                break
        return ret

    def broadcast_sum(self, ip_pool: list, partial_sum: list):
        if len(ip_pool) != self.count:
            raise Exception("Number of parties is too less.")
        for sh_idx in range(self.count):
            send_info = " ".join(str(val) for val in partial_sum).encode('utf-8')
            dest_addr = (ip_pool[sh_idx][0], ip_pool[sh_idx][1])
            self.socket.sendto(send_info, dest_addr)
            print("Client {}:{} broadcast the partial sum {} to client {}:{}".format(
                self.ip_addr, self.ip_port, send_info, dest_addr[0], dest_addr[1]
            ))

    def aggregate(self, sharing: AddSecretShare) -> list:
        w_len = len(self.weight)
        ret, cnt = [0] * w_len, 0
        while True:
            try:
                self.socket.settimeout(30)
                recv_msg, recv_ip = self.socket.recvfrom(4096)
                recv_msg = recv_msg.decode('utf-8')
                print("Client {}:{} receives the partial sum {} from client {}".format(
                    self.ip_addr, self.ip_port, recv_msg, recv_ip
                ))
                Client.agg_shares(sharing, ret, recv_msg, w_len)
            except socket.timeout:
                if cnt >= self.count:
                    print("Receive task is finished.")
                else:
                    print("Receive data timeout, break...")
                break
        return ret

    def close_socket(self):
        self.socket.close()
