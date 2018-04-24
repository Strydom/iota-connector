# Kubernetes IOTA Node Discovery

This connector runs within a Kubernetes cluster and listens to the event stream for `list_pod_for_all_namespaces`
filtering on `label_selector='type=node'`.

It uses the pod IP's from the events to connect the IOTA nodes together as neighbours.
When a new IP is discovered it is added to the previously discovered nodes and them to it.

## This repository is used by
- [kubernetes-private-iota](https://github.com/Strydom/kubernetes-private-iota)
