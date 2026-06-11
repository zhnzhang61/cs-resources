#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <algorithm>
#include <numeric>
#include <climits>
#include <cmath>
#include <sstream>
#include <cassert>

// ================= LeetCode Common Data Structures =================

struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

// ================= Helper Functions for Local Testing =================

// Linked List helpers
ListNode* listToLinkedList(const std::vector<int>& nums) {
    ListNode dummy(0);
    ListNode* curr = &dummy;
    for (int num : nums) {
        curr->next = new ListNode(num);
        curr = curr->next;
    }
    return dummy.next;
}

std::vector<int> linkedListToList(ListNode* head) {
    std::vector<int> res;
    ListNode* curr = head;
    while (curr) {
        res.push_back(curr->val);
        curr = curr->next;
    }
    return res;
}

void freeLinkedList(ListNode* head) {
    while (head) {
        ListNode* temp = head;
        head = head->next;
        delete temp;
    }
}

void printList(ListNode* head) {
    ListNode* curr = head;
    while (curr) {
        std::cout << curr->val << (curr->next ? " -> " : "");
        curr = curr->next;
    }
    std::cout << std::endl;
}

// Binary Tree helpers
TreeNode* listToBinaryTree(const std::vector<std::string>& arr) {
    if (arr.empty() || arr[0] == "null" || arr[0] == "None" || arr[0] == "") {
        return nullptr;
    }
    
    TreeNode* root = new TreeNode(std::stoi(arr[0]));
    std::queue<TreeNode*> q;
    q.push(root);
    size_t i = 1;
    
    while (!q.empty() && i < arr.size()) {
        TreeNode* curr = q.front();
        q.pop();
        
        // Left child
        if (i < arr.size()) {
            if (arr[i] != "null" && arr[i] != "None" && arr[i] != "") {
                curr->left = new TreeNode(std::stoi(arr[i]));
                q.push(curr->left);
            }
            i++;
        }
        
        // Right child
        if (i < arr.size()) {
            if (arr[i] != "null" && arr[i] != "None" && arr[i] != "") {
                curr->right = new TreeNode(std::stoi(arr[i]));
                q.push(curr->right);
            }
            i++;
        }
    }
    return root;
}

std::vector<std::string> binaryTreeToList(TreeNode* root) {
    std::vector<std::string> res;
    if (!root) return res;
    
    std::queue<TreeNode*> q;
    q.push(root);
    
    while (!q.empty()) {
        TreeNode* curr = q.front();
        q.pop();
        
        if (curr) {
            res.push_back(std::to_string(curr->val));
            q.push(curr->left);
            q.push(curr->right);
        } else {
            res.push_back("null");
        }
    }
    
    // Trim trailing "null"s
    while (!res.empty() && res.back() == "null") {
        res.pop_back();
    }
    return res;
}

void freeBinaryTree(TreeNode* root) {
    if (!root) return;
    freeBinaryTree(root->left);
    freeBinaryTree(root->right);
    delete root;
}

void printTree(TreeNode* root, std::string indent = "", bool isLeft = true) {
    if (!root) return;
    
    if (root->right) {
        printTree(root->right, indent + (isLeft ? "│   " : "    "), false);
    }
    
    std::cout << indent << (isLeft ? "└── " : "┌── ") << root->val << std::endl;
    
    if (root->left) {
        printTree(root->left, indent + (isLeft ? "    " : "│   "), true);
    }
}

// Helper to print standard vectors
template <typename T>
void printVector(const std::vector<T>& vec) {
    std::cout << "[";
    for (size_t i = 0; i < vec.size(); ++i) {
        std::cout << vec[i] << (i + 1 < vec.size() ? ", " : "");
    }
    std::cout << "]" << std::endl;
}


// ================= Solution Class =================

class Solution {
public:
    std::vector<int> twoSum(std::vector<int>& nums, int target) {
        // Example solution (Two Sum)
        std::unordered_map<int, int> seen;
        for (int i = 0; i < nums.size(); ++i) {
            int diff = target - nums[i];
            if (seen.count(diff)) {
                return {seen[diff], i};
            }
            seen[nums[i]] = i;
        }
        return {};
    }
};


// ================= Local Runner =================

int main() {
    Solution sol;
    
    // Test Case 1
    {
        std::cout << "--- Test Case 1 ---" << std::endl;
        std::vector<int> nums = {2, 7, 11, 15};
        int target = 9;
        std::vector<int> expected = {0, 1};
        
        std::vector<int> result = sol.twoSum(nums, target);
        
        assert(result == expected && "Test Case 1 Failed!");
        std::cout << "Test Case 1 Passed!\n" << std::endl;
    }
    
    // Test Case 2 (Template placeholder)
    /*
    {
        std::cout << "--- Test Case 2 ---" << std::endl;
        std::vector<int> nums = {3, 2, 4};
        int target = 6;
        std::vector<int> expected = {1, 2};
        
        std::vector<int> result = sol.twoSum(nums, target);
        
        assert(result == expected && "Test Case 2 Failed!");
        std::cout << "Test Case 2 Passed!\n" << std::endl;
    }
    */
    
    std::cout << "All tests run successfully!" << std::endl;
    return 0;
}
