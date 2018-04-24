from kubernetes import client, config, watch
from iota import Iota
import urllib3
import threading
import time


ERROR_MSG = "Error connecting to: http://{0}:14265. " \
            "- Retrying in {1} seconds - {2} retries left"


class Node:
    def __init__(self, ip):
        self.ip = ip
        self.connected_nodes = []


def main():
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    rv = 0  # resource version
    delay = 30  # number of seconds between retries
    retries = 10
    w = watch.Watch()

    discovered_nodes = []
    nodes = []

    print("Starting event watcher...")
    while True:
        try:
            for event in w.stream(v1.list_pod_for_all_namespaces, label_selector='type=node', resource_version=rv):
                pod = event['object']
                pod_ip = pod.status.pod_ip
                version = pod.metadata.resource_version

                print("Event: {0} {1}".format(event['type'], pod.metadata.name))

                if pod_ip is not None:
                    print("Pod IP: {0}".format(pod_ip))

                    # New Node has been discovered
                    if pod_ip not in discovered_nodes:
                        print("New node discovered: {0}".format(pod_ip))
                        new_node = Node(pod_ip)
                        nodes.append(new_node)
                        discovered_nodes.append(pod_ip)

                        for node in nodes:
                            # Add already discovered nodes to new node
                            if node.ip == pod_ip:
                                for alt_node in nodes:
                                    if alt_node.ip != node.ip and alt_node.ip not in node.connected_nodes:
                                        NodeConnectionThread(node, alt_node, delay, retries).start()

                            # Add new node to already discovered nodes
                            else:
                                if pod_ip not in node.connected_nodes:
                                    NodeConnectionThread(node, new_node, delay, retries).start()

                if version is not None:
                    rv = int(version)

        except urllib3.exceptions.ReadTimeoutError:
            print("Socket read timeout error. restarting watcher...")
            continue
        except Exception as e:
            """ Fatal error """
            print("Watcher error: {0}".format(e))


class NodeConnectionThread(threading.Thread):
    def __init__(self, node_a, node_b, delay, retries):
        threading.Thread.__init__(self)
        self.node_a = node_a
        self.node_b = node_b
        self.delay = delay
        self.retries = retries

    def run(self):
        node_a_ip = self.node_a.ip
        node_b_ip = self.node_b.ip
        print_t(node_a_ip, "Starting thread...")
        print_t(node_a_ip, "Adding node {0} as a neighbour to {1}".format(node_b_ip, node_a_ip))
        print_t(node_a_ip, "Attempting to connect to node: http://{0}:14265".format(node_a_ip))

        try_again = True

        while try_again and self.retries > 0:
            try:
                api = Iota("http://{0}:14265".format(node_a_ip))
                api.add_neighbors(["udp://{0}:14777".format(node_b_ip)])
                self.node_a.connected_nodes.append(node_b_ip)
                print_t(node_a_ip, "Added node {0} as a neighbour to {1}".format(node_b_ip, node_a_ip))
                try_again = False
            except:
                self.retries -= 1
                print_t(node_a_ip, ERROR_MSG.format(node_a_ip, self.delay, self.retries))
                try_again = True
                if self.retries != 0:
                    time.sleep(self.delay)

        print_t(node_a_ip, "Exiting thread.")


def print_t(thread_id, message):
    print("Thread-{0}: {1}".format(thread_id, message))


if __name__ == '__main__':
    main()
