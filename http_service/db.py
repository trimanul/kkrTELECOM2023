import redis

class budgetDAO:
    def __init__(self, url="redis://localhost"):
        self._conn = redis.from_url(url, decode_responses=True)

    def get_node_list(self):
        data = {}
        ips = self._conn.keys()

        for ip in ips:
            data[ip] = self._conn.get(ip)

        return data

    def get_node(self, ip):
        return {
            ip: self._conn.get(ip)
        }
