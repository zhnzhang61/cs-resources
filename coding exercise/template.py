#!/usr/bin/env python3
import collections
import heapq
import math
import bisect
from typing import List, Optional, Dict, Set, Tuple

# ================= LeetCode Common Data Structures =================

class ListNode:
    """Definition for singly-linked list."""
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        curr = self
        vals = []
        while curr:
            vals.append(str(curr.val))
            curr = curr.next
        return " -> ".join(vals) if vals else "Empty List"


class TreeNode:
    """Definition for a binary tree node."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return f"TreeNode({self.val})"


# ================= Helper Functions for Local Testing =================

def list_to_linked_list(nums: List[int]) -> Optional[ListNode]:
    """Converts a standard Python list to a ListNode linked list."""
    dummy = ListNode(0)
    curr = dummy
    for num in nums:
        curr.next = ListNode(num)
        curr = curr.next
    return dummy.next


def linked_list_to_list(head: Optional[ListNode]) -> List[int]:
    """Converts a ListNode linked list back to a standard Python list."""
    res = []
    curr = head
    while curr:
        res.append(curr.val)
        curr = curr.next
    return res


def list_to_binary_tree(arr: List[Optional[int]]) -> Optional[TreeNode]:
    """
    Converts a LeetCode-style level-order list (including None for null nodes)
    into a TreeNode binary tree.
    Example: list_to_binary_tree([1, None, 2, 3])
    """
    if not arr or arr[0] is None:
        return None
    
    root = TreeNode(arr[0])
    queue = collections.deque([root])
    i = 1
    
    while queue and i < len(arr):
        curr = queue.popleft()
        
        # Left child
        if i < len(arr):
            if arr[i] is not None:
                curr.left = TreeNode(arr[i])
                queue.append(curr.left)
            i += 1
            
        # Right child
        if i < len(arr):
            if arr[i] is not None:
                curr.right = TreeNode(arr[i])
                queue.append(curr.right)
            i += 1
            
    return root


def binary_tree_to_list(root: Optional[TreeNode]) -> List[Optional[int]]:
    """Converts a TreeNode binary tree back to a LeetCode level-order list."""
    if not root:
        return []
        
    res = []
    queue = collections.deque([root])
    
    while queue:
        curr = queue.popleft()
        if curr:
            res.append(curr.val)
            queue.append(curr.left)
            queue.append(curr.right)
        else:
            res.append(None)
            
    # Trim trailing Nones to match LeetCode output style
    while res and res[-1] is None:
        res.pop()
        
    return res


def print_tree(root: Optional[TreeNode], indent: str = "", is_left: bool = True) -> None:
    """Helper to visualize tree structure in console."""
    if root is None:
        return
    
    if root.right:
        print_tree(root.right, indent + ("│   " if is_left else "    "), False)
        
    print(indent + ("└── " if is_left else "┌── ") + str(root.val))
    
    if root.left:
        print_tree(root.left, indent + ("    " if is_left else "│   "), True)


# ================= Solution Class =================

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Example solution (Two Sum)
        seen = {}
        for i, num in enumerate(nums):
            diff = target - num
            if diff in seen:
                return [seen[diff], i]
            seen[num] = i
        return []


# ================= Local Runner =================

if __name__ == '__main__':
    import sys
    
    sol = Solution()
    
    # Automatically find the public solver method on Solution (ignoring helper/private methods)
    methods = [m for m in dir(sol) if not m.startswith('_') and callable(getattr(sol, m))]
    if not methods:
        print("Error: No public solver method found in Solution class!")
        sys.exit(1)
        
    method_name = methods[0]
    solve = getattr(sol, method_name)
    print(f"Running tests for: Solution.{method_name}()\n")

    # Define your test cases: [ (inputs, expected_output), ... ]
    # - If your method takes a single argument, pass it directly or wrap in a tuple: (arg,)
    # - If your method takes multiple arguments, pass them as a tuple: (arg1, arg2, ...)
    test_cases = [
        # Test Case 1: nums = [2, 7, 11, 15], target = 9 -> expected = [0, 1]
        ( ([2, 7, 11, 15], 9), [0, 1] ),
    ]

    for i, (args, expected) in enumerate(test_cases, 1):
        print(f"--- Test Case {i} ---")
        # Ensure args is a tuple for dynamic unpacking
        if not isinstance(args, tuple):
            args = (args,)
            
        # Try to print input arguments nicely
        readable_input = args[0] if len(args) == 1 else args
        print(f"Input:    {readable_input}")
        
        result = solve(*args)
        
        print(f"Result:   {result}")
        print(f"Expected: {expected}")
        
        assert result == expected, f"Test Case {i} Failed!"
        print(f"Test Case {i} Passed!\n")
        
    print("All tests run successfully!")

