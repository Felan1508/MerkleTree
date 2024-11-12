import hashlib
from math import ceil, log2
import networkx as nx
import matplotlib.pyplot as plt
import json


class MerkleTree:
    def __init__(self, data_list):
        """Initializes the Merkle Tree with a list of data, which can be complex records (dictionaries)."""
        self.leaves = [self._hash_data(data) for data in data_list]
        self.tree = self._build_tree(self.leaves)


    def _hash_data(self, data):
         """Creates a SHA-256 hash of the input data, handling both strings and dictionaries."""
         if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)  # Serialize dictionary to JSON string
         elif isinstance(data, str):
            data = data.encode('utf-8')
         else:
            data = str(data).encode('utf-8')  # Handle other types as strings
         return hashlib.sha256(data).hexdigest()

    def _build_tree(self, leaves):
        """Constructs the Merkle Tree and returns it as a list of lists."""
        tree = [leaves]
        current_level = leaves
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = left + right
                next_level.append(self._hash_data(combined))
            tree.append(next_level)
            current_level = next_level
        return tree
    
    def get_root(self):
        """Returns the Merkle root."""
        return self.tree[-1][0] if self.tree else None
    def get_tree_height(self):
        return len(self.tree)
    
    
    def visualize_tree(self):
        """Prints the Merkle tree structure level by level with hashes truncated to the first 6 characters."""
        for level_index, level in enumerate(self.tree):
            print(f"Level {level_index}:")
            print("  " + "  ".join(node[:6] for node in level))
            print()
    
    def get_proof(self, index):
        """Generates a Merkle proof for a leaf at a given index."""
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Index out of bounds")
        proof = []
        for level in range(len(self.tree) - 1):
            sibling_index = index ^ 1  # XOR with 1 toggles the last bit
            if sibling_index < len(self.tree[level]):
                position = 'left' if sibling_index < index else 'right'
                proof.append({'hash': self.tree[level][sibling_index], 'position': position})
            index //= 2
        return proof
    
    def verify_proof(self, leaf, proof, root):
        """Verifies a Merkle proof for a given leaf and root."""
        current_hash = self._hash_data(leaf)
        for sibling in proof:
            if sibling['position'] == 'left':
                current_hash = self._hash_data(sibling['hash'] + current_hash)
            elif sibling['position'] == 'right':
                current_hash = self._hash_data(current_hash + sibling['hash'])
        return current_hash == root
    
    def get_level_nodes(self, level):
        """Returns all node hashes at a specific level in the Merkle Tree."""
        if level < 0 or level >= len(self.tree):
            raise IndexError("Level out of bounds")
        return self.tree[level]
    
    def find_sibling(self, index):
        """Returns the sibling hash of a node at a given index."""
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Index out of bounds")

        # Calculate the sibling index
        sibling_index = index ^ 1  # XOR with 1 toggles the last bit, finding the sibling
        if sibling_index < len(self.leaves):
            return self.tree[0][sibling_index]
        return None
    
    def check_integrity(self):
        """Verifies the integrity of the entire Merkle Tree by ensuring each node matches the combined hash of its children."""
        def combine_hashes(left, right):
            # Helper function to combine two hashes
            if left is None:
                return self._hash_data(right)
            if right is None:
                return self._hash_data(left)
            return self._hash_data(left + right)
        
        # Iterate from the second last level up to the root
        for level in range(len(self.tree) - 2, -1, -1):
            for i in range(0, len(self.tree[level]), 2):
                # Get left and right child hashes
                left = self.tree[level][i]
                right = self.tree[level][i + 1] if i + 1 < len(self.tree[level]) else left
                # Calculate the expected parent hash
                expected_parent_hash = combine_hashes(left, right)
                # Check if the calculated hash matches the actual parent hash
                if expected_parent_hash != self.tree[level + 1][i // 2]:
                    return False  # Integrity check failed
        return True  # Integrity is intact
    
    def test_immutability(self, index, new_value):
        """Tests the immutability of the Merkle Tree by modifying a leaf node and checking if the Merkle Root changes."""
        # Store the original root hash
        original_root = self.get_root()

        # Temporarily modify the leaf at the given index
        original_leaf = self.leaves[index]
        self.leaves[index] = self._hash_data(new_value)

        # Rebuild the tree with the modified leaf
        self.tree = self._build_tree(self.leaves)

        # Check the new root hash
        updated_root = self.get_root()

        # Restore the original leaf value and rebuild the tree
        self.leaves[index] = original_leaf
        self.tree = self._build_tree(self.leaves)

        # Return whether the roots match
        return original_root == updated_root
    


    

    
    
if __name__ == "__main__":
    data = ['a', 'b']
    merkle_tree = MerkleTree(data)
    print("Merkle Tree:", merkle_tree.tree)
    print("Merkle Tree Leaves:", merkle_tree.leaves)
    proof = merkle_tree.get_proof(1)
    is_valid = merkle_tree.verify_proof('b', proof , merkle_tree.get_root())
    print("\nProof is valid:", is_valid)
    nodes_at_level_1 = merkle_tree.get_level_nodes(1)
    print("Nodes at Level 1:", nodes_at_level_1)
    sibling_hash = merkle_tree.find_sibling(2)
    print("Sibling of node 2:", sibling_hash)
    is_tree_valid = merkle_tree.check_integrity()
    print("Is the tree integrity intact?", is_tree_valid)
    merkle_tree.visualize_tree()
    index_to_modify = 2
    new_value = 'z'
    roots_match = merkle_tree.test_immutability(index_to_modify, new_value)
    print("Roots match after modification:", roots_match)  # Expected: False

    records = [
    {"id": 1, "name": "Alice", "balance": 100.50},
    {"id": 2, "name": "Bob", "balance": 200.00},
    {"id": 3, "name": "Charlie", "balance": 150.75}
]

merkle_tree = MerkleTree(records)
root = merkle_tree.get_root()
proof = merkle_tree.get_proof(1)
is_valid = merkle_tree.verify_proof(records[1], proof, root)

print("Root hash:", root)
print("Proof for record 1 is valid:", is_valid)  # Expected: True

