from asciitree import LeftAligned
from asciitree.drawing import BoxStyle, BOX_LIGHT

def dictify_tree(node):
    if not node.children:
        return {}  # If there are no children, return an empty dict.
    else:
        # Join the dictionary keys into a tuple
        return {(tuple(child.value), child.idx): dictify_tree(child) for child in node.children}

class TreeNode:
    treewidth = -1

    def __init__(self, value, idx = 0):
        self.value = value  # Nodes
        self.children = []  # TreeNode
        self.idx = idx
        self.node_order = {node: i for i, node in enumerate(self.value)}
        if self.treewidth == -1:
            print("ERROR")
        self.S = [i for i in range(2**(self.treewidth + 1))]
        self.f_t = [0 for _ in range(2**(self.treewidth + 1))]

    def forget_step(self, index, forgotten):
        # Forget node
        child_index = index
        for node in self.node_order.keys():
            i = self.node_order[node]
            j = self.children[0].node_order[node]
            if ((child_index >> i) & 1) != ((child_index >> j) & 1):    # Only flip if different
                bit_mask = (1 << i) | (1 << j)
                child_index ^= bit_mask
        second_index = child_index
        bit_mask = (1 << self.children[0].node_order[forgotten])
        second_index ^= bit_mask
        self.f_t[index] = max(self.children[0].f_t[child_index], self.children[0].f_t[second_index])
        
    def introduce_step(self, index, introduced):
        # Introduce node
        child_index = index

        if (self.S[index] >> self.node_order[introduced]):
            child_index ^= (1 << self.node_order[introduced])
            for node in self.children[0].node_order.keys():
                i = self.node_order[node]
                j = self.children[0].node_order[node]
                if ((child_index >> i) & 1) != ((child_index >> j) & 1):    # Only flip if different
                    bit_mask = (1 << i) | (1 << j)
                    child_index ^= bit_mask
            self.f_t[index] = self.children[0].f_t[child_index] + 1
        else:
            for node in self.children[0].node_order.keys():
                i = self.node_order[node]
                j = self.children[0].node_order[node]
                if ((child_index >> i) & 1) != ((child_index >> j) & 1):    # Only flip if different
                    bit_mask = (1 << i) | (1 << j)
                    child_index ^= bit_mask
            self.f_t[index] = self.children[0].f_t[child_index]

    def add_child(self, child_node):
        self.children.append(child_node)

    def insert_node(self, bag, index = 0):
        """Insert bag inbetween old nodes"""
        old_node = self.children.pop()
        new_node = TreeNode(bag, index)
        new_node.add_child(old_node)
        self.add_child(new_node)

    def make_join_node(self):
        first_child = self.children.pop()
        second_child = self.children.pop()
        first_join_node = TreeNode(self.value, first_child.idx)      # TODO: copy self.value?
        second_join_node = TreeNode(self.value, second_child.idx)
        first_join_node.add_child(first_child)
        second_join_node.add_child(second_child)
        self.add_child(first_join_node)
        self.add_child(second_join_node)

    def number_of_nodes(self):
        return 1 + sum([child.number_of_nodes() for child in self.children])

    def __str__(self, level=0):
        ret = "\t" * level + repr(self.idx) + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

def parseTree(filename, G):
    f = open(filename + ".td")

    bags = {}
    bag_edges = []

    for line in f:
        match line[0]:
            case 'c':
                # Skip comments
                continue
            case 's':
                # Bag and graph information, note treewidth + 1
                nr_bags, treewidth, nr_nodes = map(lambda x: int(x), line.split(" ")[2:])
            case 'b':
                # Bag, take subgraph with nodes
                l = line.split(" ")
                bag_nr = int(l[1])
                nodes = set(map(lambda x: int(x), l[2:]))
                bags[bag_nr] = nodes
            case x if x.isdigit():
                # Edge
                bag_edges.append(list(map(lambda x : int(x), line.split(" "))))
            case _:
                print("ERROR ", line)
                break
    
    TreeNode.treewidth = treewidth

    for i in range(1, nr_bags + 1):
        if bags[i]:
            root = TreeNode(bags.pop(i), i)
            break
    f.close()
    
    while bag_edges:
        buildTree(bags, bag_edges, root, root.idx)

    return root

def buildTree(bags, bag_edges, current_node, current_idx):
    for i, edge in enumerate(bag_edges):
        if edge[0] == current_idx:
            current_node.add_child(TreeNode(bags.pop(edge[1]), edge[1]))
            bag_edges.pop(i)
        elif edge[1] == current_idx:
            current_node.add_child(TreeNode(bags.pop(edge[0]), edge[0]))
            bag_edges.pop(i)
    for child in current_node.children:
        buildTree(bags, bag_edges, child, child.idx)

def loadGraph(file):
    f = open(file + ".gr")
    edges = []
    for line in f:
        match line[0]:
            case 'c':
                # Comment, skip
                continue
            case 'p':
                nr_nodes, nr_edges = map(lambda x : int(x), line.split(" ")[2:])
            case x if x.isdigit():
                edge = line.split(" ")
                edge = [int(node) for node in edge]
                edges.append(edge)
    G = {i: [] for i in range(1, nr_nodes + 1)}
    for node1, node2 in edges:
        G[node1].append(node2)
        G[node2].append(node1)
    f.close()
    return G

def insert_leaf_bags(node):
    if not node.children:
        node.add_child(TreeNode(set()))
    else:
        for child in node.children:
            insert_leaf_bags(child)

def insert_join_bags(node):
    if len(node.children) == 2:
        node.make_join_node()
    for child in node.children:
        insert_join_bags(child)

def insert_forget_bags(node):
    children = node.children.copy()
    if len(node.children) == 1:
        bag = node.value & node.children[0].value
        bag_lenght = len(bag)
        if (bag_lenght != len(node.children[0].value) and bag_lenght != len(node.value)) and bag_lenght != 0:
            node.insert_node(bag)
    for child in children:
        insert_forget_bags(child)

def insert_introduce_bags(node):
    children = node.children.copy()
    if len(node.children) == 1:
        if len(node.value) > len(node.children[0].value):
            difference = node.value - (node.value & node.children[0].value)
            if len(difference) > 1:
                bag = node.children[0].value | {difference.pop()}
                node.insert_node(bag, -2)
        else:
            difference = node.children[0].value - (node.value & node.children[0].value)
            if len(difference) > 1:
                bag = node.value | {difference.pop()}
                node.insert_node(bag, -2)
    for child in children:
        insert_introduce_bags(child)
        
def niceifyTree(root):
    insert_leaf_bags(root)
    insert_join_bags(root)
    while True:
        nr_nodes = root.number_of_nodes()
        insert_forget_bags(root)
        insert_introduce_bags(root)
        if root.number_of_nodes() - nr_nodes == 0:
            break

    return

def type_of_node(node):
    if not node.children:
        return 0 # Leaf node
    
    match (len(node.value) - len(node.children[0].value)):
        case x if x < 0:
            # Forget node
            return 1
        case x if x > 0:
            # Introduce node
            return 2
        case x if x == 0:
            # Join node
            return 3
        case _:
            print("ERROR")
            return
        
def check_independent(G, S):
    for node in S:
        if set(G[node]) & set(S):
            return False
    return True

def selected_nodes(G, nodes, i):
    index = i
    active_nodes = []
    current = len(nodes)
    nodes_copy = list(nodes)
    while current > 0:
        if index & 1:
            active_nodes.append(nodes_copy.pop())
        current -= 1
        index = (index >> 1)
    return active_nodes

def c(node, G):
    node_type = type_of_node(node)
    match node_type:
        case 0:
            return 0
        case 1:
            # Forget node
            forgotten_node = (node.children[0].value - node.value).pop()
            c(node.children[0], G)
            for i in node.S:
                if check_independent(G, selected_nodes(G, node.value, i)):
                    node.forget_step(i, forgotten_node)
                else:
                    node.f_t[i] = -10**10
        case 2:
            introduced_node = (node.value - node.children[0].value).pop()
            c(node.children[0], G)
            for i in node.S:
                if check_independent(G, selected_nodes(G, node.value, i)):
                    node.introduce_step(i, introduced_node)       # Introduced_node only has 1 element
                else:
                    node.f_t[i] = -10**10
        case 3:
            c(node.children[0], G)
            c(node.children[1], G)
            for i in node.S:
                # if check_independent(G, selected_nodes(G, node.value), i):    # Assume independant?
                node.f_t[i] = node.children[0].f_t[i] + node.children[1].f_t[i] - len(selected_nodes(G, node.value, i))
        case _:
            print("ERROR")
            return

# file = "data/eppstein"
file = "data/web4"
G = loadGraph(file)
root = parseTree(file, G)

tree_dict = {(tuple(root.value), 1): dictify_tree(root)}

# Draw the tree using asciitree
tr = LeftAligned(draw=BoxStyle(gfx=BOX_LIGHT, horiz_len=3))
print(tr(tree_dict))

niceifyTree(root)

# Convert your custom tree structure to a dictionary format
tree_dict = {(tuple(root.value), 1): dictify_tree(root)}

# Draw the tree using asciitree
tr = LeftAligned(draw=BoxStyle(gfx=BOX_LIGHT, horiz_len=3))
print(tr(tree_dict))


# Calculate independent set
c(root, G)
print(root.f_t)
