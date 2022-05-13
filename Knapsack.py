#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import sys, math

Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])
problem_LB = 0
nnodes = 0
smallest = 0
items = []
capacity = 0

class Node:
    def __init__(self, upper_bound, room, value, index):
        self.left = None
        self.UB = upper_bound
        self.room = room
        self.value = value
        self.index = index
        self.right = None

class Tree:
    def CreateNode(self, upper_bound, room, total_value, index):
        global nnodes
        nnodes = nnodes + 1
        return Node(upper_bound, room, total_value, index)

    def PrintTree(self, node):
        if self is None:
            return

        print("UB: " + str(node.UB) + " K: " + str(node.room) + " V: " + str(node.value) + " Ind:"  + str(node.index) +
              " " + str(items[node.index]))
        if node.left is not None:
            self.PrintTree(node.left)
        if node.right is not None:
            self.PrintTree(node.right)

    def insert(self, node, item, nrights):
        global problem_LB
        global smallest
        index_next_item = node.index + 1

        if node.left is not None and node.left.room >= smallest and node.left.UB >= problem_LB:
            self.insert(node.left, item, 0)
        elif node.left is None:
            keep_capacity = node.room - items[index_next_item].weight
            if keep_capacity >= 0:
                if node.UB >= problem_LB:
                    value = node.value + items[index_next_item].value
                    node.left = self.CreateNode(node.UB, keep_capacity, value, index_next_item)
                    problem_LB = max(problem_LB, value)
            else:
                node.UB = EstimateUpperBound(index_next_item + 1, node.room, node.value)

        if node.UB < problem_LB:
            return


        if node.right is not None:
            if node.right.room < smallest:
                node.right.UB = node.value
                return
            else:
                self.insert(node.right, item, nrights + 1)
        elif node.right is None and node.UB >= problem_LB:
            hx = EstimateUpperBound(index_next_item + 1, node.room, node.value)
            if hx >= problem_LB and node.room > smallest:
                if node.left is None or node.left.UB < problem_LB or node.left.room <= 0:
                    node.left = None
                    node.UB = hx

                    # combine consecutive right nodes to avoid hitting recursion limit
                    if nrights > 2:
                        node.index = index_next_item
                        return

                node.right = self.CreateNode(hx, node.room, node.value, index_next_item)


    def search(self, node, value, x):
        global problem_LB

        if node.UB < problem_LB:
            node = None
            return value

        if node.left is not None:
            itemvalue = items[node.left.index].value

            cumval = self.search(node.left, value + itemvalue, x)
            if cumval == problem_LB:
                x[node.left.index] = 1
                return cumval

        if node.right is not None:
            return self.search(node.right, value, x)

        return value

def EstimateUpperBound(start_index, room, total_value):
    global capacity
    global items

    estimate = total_value

    for i in range(start_index, len(items)):
        if room <= 0:
            break
        if room - items[i].weight >= 0:
            room = room - items[i].weight
            estimate = estimate + items[i].value
        else:
            if items[i].weight <= capacity and room > 0:
                frac = room / items[i].weight
                estimate = estimate + frac * items[i].value
                room = 0

    return estimate

def SmallestItem(minsize, items):
    global capacity
    smallest = capacity

    for i in range(1, len(items)):
        if items[i].weight > minsize:
            smallest = min(smallest, items[i].weight)

    return smallest

def Solve(input_data):
    global capacity
    global items
    global problem_LB
    global smallest

    problem_LB = 0
    smallest = 0
    capacity = 0
    items = []

    lines = input_data.split('\n')
    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    for i in range(1, item_count + 1):
        line = lines[i]
        parts = line.split()
        value = int(parts[0])
        weight = int(parts[1])
        density = float(value) / float(weight)
        if weight > capacity:
            density = 0
        items.append(Item(i - 1, int(parts[0]), int(parts[1]), density))


    smallest = SmallestItem(0, items)

    taken = [0] * len(items)
    taken_permute = [0] * len(taken)

    items.sort(key = lambda items:items[3], reverse=True)

    tb = Tree()
    upper_bound = EstimateUpperBound(0, capacity, 0)
    root = tb.CreateNode(upper_bound, capacity, 0, -1)

    for i in range(0, item_count):
        if items[i].weight <= capacity:
            tb.insert(root, items[i], 0)
            #if i % 10 == 0:
            #    print(str(i) + " " + str(nnodes) + " " + str(problem_LB) + " " + str(problem_LB))

        if items[i].weight == smallest:
            smallest = SmallestItem(items[i].weight, items)


    tb.search(root, 0, taken_permute)
    for i in range(0, item_count):
        taken[items[i].index] = taken_permute[i]


    weight = 0
    value = 0
    for item in items:
        value += item.value * taken[item.index]
        weight += item.weight * taken[item.index]

    output_data = str(value) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))

    print("Total Value: " + str(value))
    print("Weight: "  + str(weight))
    print("Nodes: " + str(nnodes))
    print(output_data)

    return output_data

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(Solve(input_data))
    else:
        print(
            'This test requires an input file.  Please select one from the data directory. (i.e. python Knapsack.py ./data/test_10)')

