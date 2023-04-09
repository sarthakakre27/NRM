import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from file_parser import parseFileGraphCreation

# function to find node with max bid, nodes are in the form of ('node_name': str, bid: int)
def find_max_bid(graph, source):
    # find the node with max bid, there can be multiple nodes with same bid
    max_bids = []
    max_bid = 0
    # for node in graph.nodes:
    #     if node[1] > max_bid:
    #         max_bid = node[1]
    #         node_name = node[0]
    # return (node_name, max_bid)
    for node in graph.nodes:
        if node[1] > max_bid:
            max_bid = node[1]
            max_bids = [node]
        elif node[1] == max_bid:
            max_bids.append((node[0], node[1]))
    
    # print(max_bids)
    # find which node is closer to the source
    min_distance = 100000
    min_node = None
    for node in max_bids:
        distance = nx.shortest_path_length(graph, source, node)
        if distance < min_distance:
            min_distance = distance
            min_node = node
    return min_node

def find_max_bid_without_node(graph, source, node_to_remove):
    # find the node with max bid, there can be multiple nodes with same bid
    G_temp = graph.copy()
    # remove node_to_remove and all nodes such that, if node_to_remove is removed, then the node is not connected to the source
    if type(node_to_remove) == list:
        for node in node_to_remove:
            G_temp.remove_node(node)
    else:
        G_temp.remove_node(node_to_remove)
    for node in graph.nodes:
        try:
            if not nx.has_path(G_temp, source, node):
                G_temp.remove_node(node)
        except:
            pass
    print(G_temp.nodes)
    max_bids = []
    max_bid = 0
    for node in G_temp.nodes:
        if node[1] > max_bid:
            max_bid = node[1]
            max_bids = [node]
        elif node[1] == max_bid:
            max_bids.append((node[0], node[1]))
        
    # print(max_bids)
    # find which node is closer to the source
    min_distance = 100000
    min_node = None
    for node in max_bids:
        distance = nx.shortest_path_length(G_temp, source, node)
        if distance < min_distance:
            min_distance = distance
            min_node = node
    
    G_temp.clear()
    del G_temp
    return min_node


def find_all_paths(graph, source, target):
    all_paths = list(nx.all_simple_paths(graph, source, target))
    return all_paths


def find_intersection(graph, source, all_paths):
    # find the intersection of all paths
    intersection = set(all_paths[0])
    for path in all_paths:
        intersection = intersection.intersection(set(path))
    
    # sort intersection by depth
    intersection = list(intersection)
    intersection.sort(key=lambda x: nx.shortest_path_length(graph, source, x))
    return intersection


def find_sibling_set(graph, intersection, source, target):
    # find the sibling set
    sibling_set = {}
    for i in range(1, len(intersection)):
        siblings = []
        # find the depth of the node
        depth = nx.shortest_path_length(graph, source, intersection[i-1])
        # find neighbors of the node
        neighbors = list(graph.neighbors(intersection[i-1]))
        # check if all the neighbors have depth + 1, else discard
        for neighbor in neighbors:
            if nx.shortest_path_length(graph, source, neighbor) == depth + 1:
                siblings.append(neighbor)
        try:
            siblings.remove(intersection[i])
        except:
            pass
        sibling_set[intersection[i]] = siblings
    return sibling_set


def calculate_nodes_in_subgraph(graph, node, source, target):
    # print("node: ", node)
    G_temp = graph.copy()
    G_temp.remove_node(node) 
    count = 1   
    for node in graph.nodes:
        try:
            if not nx.has_path(G_temp, source, node):
                G_temp.remove_node(node)
                count += 1
        except:
            pass
    G_temp.clear()
    del G_temp
    return count



def calculate(graph, common_nodes, sibling_set, source, target):
    length = len(common_nodes)
    A = common_nodes
    # print(A)
    # Pi = [0] * length
    # R = [0] * length
    # p = [0] * length
    Pi = {}
    R = {}
    p = {}

    # P_auc = [0] * length
    # P_auc[0] = 0
    P_auc = {}
    P_auc[common_nodes[0]] = 0
    S_theta = 0

    for j in range(1, length):
        print("node removed: ", A[j])
        P_auc[A[j]] = find_max_bid_without_node(graph, A[0], A[j])[1]
        print(P_auc[A[j]])
        S_aj = P_auc[A[j]] - P_auc[A[j-1]]
        print("S_aj: ", S_aj)
        X = sibling_set[A[j]].copy()
        siblings = X.copy()
        X.append(A[j])
        print("X: ", X)
        # print(calculate_nodes_in_subgraph(graph, A[j], source, target))
        n_X = 0
        for x in X:
            n_X += calculate_nodes_in_subgraph(graph, x, source, target)
        print("n_X: ", n_X)

        for k in range(len(X)):
            h_bar = find_max_bid_without_node(graph, source, X[k])
            print("h_bar: ", h_bar)
            intermediate_intersection = find_intersection(graph, source, find_all_paths(graph, source, h_bar))
            print("intermediate_intersection: ", intermediate_intersection)
            A_bar = intermediate_intersection
            print("A_bar: ", A_bar)
            try:
                if A[j-1] == A_bar[j-1]:
                    t = find_max_bid_without_node(graph, source, [A_bar[j],X[k]])[1]
                    S_k = t - P_auc[A[j-1]]
                else:
                    S_k = 0
            except:
                S_k = 0
            print("S_k: ", S_k)
            print("length", length)
            print("length of X", len(X))
            R[X[k]] = calculate_nodes_in_subgraph(graph, X[k], source, target) / n_X * S_k
            print("R[k]: ", R[X[k]])
            p[X[k]] = -1 * R[X[k]]
        
        temp_sum = 0
        for i in range(len(X)):
            temp_sum += R[X[i]]
        S_theta += S_aj - temp_sum

        if A[j][1] >= P_auc[A[j]]:
            Pi[A[j]] = 1
            p[A[j]] = P_auc[A[j]] - R[A[j]]
            break

    
    print("Pi: ", Pi)
    # print("R: ", R)
    print("p: ", p)





if __name__ == '__main__':

    # take input file name from user in argument
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="input file name")
    args = parser.parse_args()
    input_file = args.input_file

    # function call to parse the file
    G = nx.DiGraph()
    source = ('\0', -1)
    [G,source] = parseFileGraphCreation(input_file)
# o 0 a b c
# a 4 d e f o
# b 7 f g h o
# c 6 h i o
# d 6 e a
# e 3 d a
# f 9 g a b
# g 8 j k l m b f
# h 9 b c
# i 12 c
# j 15 g
# k 11 n g
# l 13 p q g
# m 9 q g
# n 14 p k
# p 16 r n l
# q 15 l m
# r 19 p
    # G = nx.Graph()
    # G.add_node(('o', 0))
    # G.add_node(('a', 4))
    # G.add_node(('b', 7))
    # G.add_node(('c', 6))
    # G.add_node(('d', 6))
    # G.add_node(('e', 3))
    # G.add_node(('f', 9))
    # G.add_node(('g', 8))
    # G.add_node(('h', 9))
    # G.add_node(('i', 12))
    # G.add_node(('j', 15))
    # G.add_node(('k', 11))
    # G.add_node(('l', 13))
    # G.add_node(('m', 9))
    # G.add_node(('n', 14))
    # G.add_node(('p', 16))
    # G.add_node(('q', 15))
    # G.add_node(('r', 19))
    # G.add_edge(('o', 0), ('a', 4))
    # G.add_edge(('o', 0), ('b', 7))
    # G.add_edge(('o', 0), ('c', 6))
    # G.add_edge(('a', 4), ('d', 6))
    # G.add_edge(('a', 4), ('e', 3))
    # G.add_edge(('a', 4), ('f', 9))
    # G.add_edge(('a', 4), ('o', 0))
    # G.add_edge(('b', 7), ('f', 9))
    # G.add_edge(('b', 7), ('g', 8))
    # G.add_edge(('b', 7), ('h', 9))
    # G.add_edge(('b', 7), ('o', 0))
    # G.add_edge(('c', 6), ('h', 9))
    # G.add_edge(('c', 6), ('i', 12))
    # G.add_edge(('c', 6), ('o', 0))
    # G.add_edge(('d', 6), ('e', 3))
    # G.add_edge(('d', 6), ('a', 4))
    # G.add_edge(('e', 3), ('d', 6))
    # G.add_edge(('e', 3), ('a', 4))
    # G.add_edge(('f', 9), ('g', 8))
    # G.add_edge(('f', 9), ('a', 4))
    # G.add_edge(('f', 9), ('b', 7))
    # G.add_edge(('g', 8), ('j', 15))
    # G.add_edge(('g', 8), ('k', 11))
    # G.add_edge(('g', 8), ('l', 13))
    # G.add_edge(('g', 8), ('m', 9))
    # G.add_edge(('g', 8), ('b', 7))
    # G.add_edge(('g', 8), ('f', 9))
    # G.add_edge(('h', 9), ('b', 7))
    # G.add_edge(('h', 9), ('c', 6))
    # G.add_edge(('i', 12), ('c', 6))
    # G.add_edge(('j', 15), ('g', 8))
    # G.add_edge(('k', 11), ('n', 14))
    # G.add_edge(('k', 11), ('g', 8))
    # G.add_edge(('l', 13), ('p', 16))
    # G.add_edge(('l', 13), ('q', 15))
    # G.add_edge(('l', 13), ('g', 8))
    # G.add_edge(('m', 9), ('q', 15))
    # G.add_edge(('m', 9), ('g', 8))
    # G.add_edge(('n', 14), ('p', 16))
    # G.add_edge(('n', 14), ('k', 11))
    # G.add_edge(('p', 16), ('r', 19))
    # G.add_edge(('p', 16), ('n', 14))
    # G.add_edge(('p', 16), ('l', 13))
    # G.add_edge(('q', 15), ('l', 13))
    # G.add_edge(('q', 15), ('m', 9))
    # G.add_edge(('r', 19), ('p', 16))


    # source = ('o', 0)
    nx.draw(G, with_labels=True)
    plt.savefig("filename.png")

    max_node = find_max_bid(G, ('o', 0))
    winner = max_node
    print(max_node)

    all_paths = find_all_paths(G, ('o', 0), max_node)
    # print(all_paths)

    common_nodes = find_intersection(G, source,all_paths)
    print(common_nodes)

    sibling_set = find_sibling_set(G, common_nodes, source, winner)
    print(sibling_set)

    calculate(G, common_nodes, sibling_set, source, winner)