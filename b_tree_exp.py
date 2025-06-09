class BTreeNode:
    def __init__(self, leaf=False):
        self.keys = []  # List of keys (primary keys or indexed values)
        self.values = []  # List of associated data records
        self.children = []  # List of child nodes
        self.leaf = leaf  # True if leaf node, False if internal node
    
    def __str__(self):
        return f"Keys: {self.keys}"

class BTree:
    def __init__(self, degree=3):
        self.root = BTreeNode(leaf=True)
        self.degree = degree  # Minimum degree (t), max keys = 2t-1, min keys = t-1
    
    def insert(self, key, value):
        """Insert a key-value pair into the B-tree"""
        print(f"\n=== INSERTING ({key}, {value}) ===")
        
        root = self.root
        
        # If root is full, create new root
        if len(root.keys) == (2 * self.degree) - 1:
            new_root = BTreeNode()
            self.root = new_root
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)
        
        print(f"After inserting ({key}, {value}):")
        self.display()
    
    def _insert_non_full(self, node, key, value):
        """Insert into a node that is not full"""
        i = len(node.keys) - 1
        
        if node.leaf:
            # Insert into leaf node
            node.keys.append(None)
            node.values.append(None)
            
            # Shift elements to maintain sorted order
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            
            node.keys[i + 1] = key
            node.values[i + 1] = value
            
            # Check if this insertion will cause a split on next insertion
            if len(node.keys) == (2 * self.degree) - 1:
                print(f"⚠️  Node is now full with {len(node.keys)} keys (max capacity reached)")
        else:
            # Find child to insert into
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            # If child is full, split it
            if len(node.children[i].keys) == (2 * self.degree) - 1:
                print(f"Child node is full, splitting required...")
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key, value)
    
    def _split_child(self, parent, index):
        """Split a full child node"""
        degree = self.degree
        full_child = parent.children[index]
        new_child = BTreeNode(leaf=full_child.leaf)
        
        # Calculate the middle index
        mid_index = degree - 1
        
        # Store the middle key and value before modifying the arrays
        mid_key = full_child.keys[mid_index]
        mid_value = full_child.values[mid_index]
        
        # Show the node before splitting with highlighted middle element
        print(f"Before splitting: {self._format_node_for_split(full_child, mid_index)}")
        
        # Move the right half of keys/values to new child
        new_child.keys = full_child.keys[degree:]
        new_child.values = full_child.values[degree:]
        
        # Keep only the left half in the original child (excluding middle)
        full_child.keys = full_child.keys[:mid_index]
        full_child.values = full_child.values[:mid_index]
        
        # Move children if not leaf
        if not full_child.leaf:
            new_child.children = full_child.children[degree:]
            full_child.children = full_child.children[:degree]
        
        # Insert the middle key into parent and add new child
        parent.children.insert(index + 1, new_child)
        parent.keys.insert(index, mid_key)
        parent.values.insert(index, mid_value)
        
        print(f"Middle element promoted: \033[91m({mid_key}, '{mid_value}')\033[0m")
    
    def _format_node_for_split(self, node, mid_index):
        """Format a node for display before splitting, highlighting the middle element"""
        node_type = "LEAF" if node.leaf else "NODE"
        formatted_pairs = []
        
        for i, (key, value) in enumerate(zip(node.keys, node.values)):
            if i == mid_index:
                # Highlight the middle element in red
                formatted_pairs.append(f"\033[91m({key}, '{value}')\033[0m")
            else:
                formatted_pairs.append(f"({key}, '{value}')")
        
        return f"{node_type}: [{', '.join(formatted_pairs)}]"
    
    def search(self, key):
        """Search for a key in the B-tree (SQL SELECT operation)"""
        print(f"\n=== SEARCHING for key {key} ===")
        result = self._search_node(self.root, key)
        if result:
            print(f"Found: Key={result[0]}, Value={result[1]}")
            return result
        else:
            print(f"Key {key} not found")
            return None
    
    def _search_node(self, node, key):
        """Recursively search for key in node"""
        i = 0
        
        # Find the first key greater than or equal to search key
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        # If key found
        if i < len(node.keys) and key == node.keys[i]:
            return (node.keys[i], node.values[i])
        
        # If leaf node and key not found
        if node.leaf:
            return None
        
        # Recursively search appropriate child
        return self._search_node(node.children[i], key)
    
    def range_search(self, start_key, end_key):
        """Search for all keys in a range (SQL SELECT with WHERE clause)"""
        print(f"\n=== RANGE SEARCH: {start_key} to {end_key} ===")
        results = []
        self._range_search_node(self.root, start_key, end_key, results)
        
        if results:
            print("Found records:")
            for key, value in results:
                print(f"  Key={key}, Value={value}")
        else:
            print("No records found in range")
        
        return results
    
    def _range_search_node(self, node, start_key, end_key, results):
        """Recursively search for keys in range"""
        i = 0
        
        # Process each key in current node
        while i < len(node.keys):
            # If not leaf, search left child first
            if not node.leaf:
                self._range_search_node(node.children[i], start_key, end_key, results)
            
            # Check if current key is in range
            if start_key <= node.keys[i] <= end_key:
                results.append((node.keys[i], node.values[i]))
            
            # If current key exceeds end_key, no need to continue
            if node.keys[i] > end_key:
                return
            
            i += 1
        
        # Search rightmost child if not leaf
        if not node.leaf:
            self._range_search_node(node.children[i], start_key, end_key, results)
    
    def display(self):
        """Display the B-tree structure"""
        print("\n--- B-Tree Structure ---")
        if self.root:
            self._display_node(self.root, 0)
        print("------------------------")
    
    def _display_node(self, node, level):
        """Recursively display node structure"""
        indent = "  " * level
        
        if node.leaf:
            print(f"{indent}LEAF: {list(zip(node.keys, node.values))}")
        else:
            print(f"{indent}NODE: {list(zip(node.keys, node.values))}")
            for child in node.children:
                self._display_node(child, level + 1)
    
    def display_tree_visual(self):
        """Display the B-tree in a visual tree format"""
        print("\n" + "="*80)
        print("VISUAL B-TREE STRUCTURE (Real Tree Format)")
        print("="*80)
        
        if not self.root:
            print("Empty tree")
            return
        
        # Calculate tree height for better formatting
        height = self._get_height(self.root)
        print(f"Tree Height: {height}")
        print()
        
        self._display_visual_node(self.root, "", True, True)
        print("="*80)
    
    def _get_height(self, node):
        """Calculate the height of the tree"""
        if node.leaf:
            return 1
        return 1 + max(self._get_height(child) for child in node.children)
    
    def _display_visual_node(self, node, prefix, is_last, is_root=False):
        """Display node in visual tree format with branches"""
        # Create the node display string
        if node.leaf:
            node_type = "🍃 LEAF"
            node_color = "\033[92m"  # Green for leaves
        else:
            node_type = "🔵 NODE" 
            node_color = "\033[94m"  # Blue for internal nodes
        
        reset_color = "\033[0m"
        
        # Format keys and values for display
        if len(node.keys) <= 3:
            content = str(list(zip(node.keys, node.values)))
        else:
            # Truncate if too many keys for clean display
            content = f"[{len(node.keys)} items: {node.keys[0]}...{node.keys[-1]}]"
        
        # Create the tree branch structure
        if is_root:
            branch = "🌳 ROOT "
            print(f"{node_color}{branch}{node_type}: {content}{reset_color}")
        else:
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{node_color}{node_type}: {content}{reset_color}")
        
        # Prepare prefix for children
        if not node.leaf and node.children:
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            # Display children
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                self._display_visual_node(child, child_prefix, is_last_child)

# Simulate SQL Database Operations using B-Tree
class SimpleSQLDatabase:
    def __init__(self):
        self.tables = {}
    
    def create_table(self, table_name, degree=3):
        """CREATE TABLE equivalent"""
        print(f"\n### Creating table '{table_name}' with B-Tree index ###")
        self.tables[table_name] = BTree(degree)
    
    def insert_record(self, table_name, key, value):
        """INSERT INTO equivalent"""
        if table_name not in self.tables:
            print(f"Table {table_name} does not exist!")
            return
        
        print(f"\nSQL: INSERT INTO {table_name} VALUES ({key}, '{value}')")
        self.tables[table_name].insert(key, value)
    
    def select_record(self, table_name, key):
        """SELECT * FROM table WHERE key = value"""
        if table_name not in self.tables:
            print(f"Table {table_name} does not exist!")
            return
        
        print(f"\nSQL: SELECT * FROM {table_name} WHERE id = {key}")
        return self.tables[table_name].search(key)
    
    def select_range(self, table_name, start_key, end_key):
        """SELECT * FROM table WHERE key BETWEEN start AND end"""
        if table_name not in self.tables:
            print(f"Table {table_name} does not exist!")
            return
        
        print(f"\nSQL: SELECT * FROM {table_name} WHERE id BETWEEN {start_key} AND {end_key}")
        return self.tables[table_name].range_search(start_key, end_key)
    
    def show_table_structure(self, table_name):
        """Show the B-tree structure of a table"""
        if table_name not in self.tables:
            print(f"Table {table_name} does not exist!")
            return
        
        print(f"\n### B-Tree structure for table '{table_name}' ###")
        self.tables[table_name].display()
        
        # Also show visual tree format
        self.tables[table_name].display_tree_visual()

def main():
    print("="*60)
    print("B-TREE DEMONSTRATION FOR SQL DATABASE OPERATIONS")
    print("="*60)
    
    # Create database instance
    db = SimpleSQLDatabase()
    
    # Create a table (with B-tree index)
    db.create_table("employees", degree=3)
    
    # Insert records (this will trigger B-tree splits as needed)
    print("\n" + "="*50)
    print("INSERTING EMPLOYEE RECORDS")
    print("="*50)
    
    employees = [
        (101, "Alice Johnson"),
        (205, "Bob Smith"),
        (150, "Carol Davis"),
        (175, "David Wilson"),
        (110, "Eva Brown"),
        (300, "Frank Miller"),
        (125, "Grace Lee"),
        (180, "Henry Clark"),
        (195, "Ivy Martinez"),
        (250, "Jack Taylor")
    ]
    
    for emp_id, name in employees:
        db.insert_record("employees", emp_id, name)
    
    # Show final B-tree structure
    print("\n" + "="*60)
    print("FINAL B-TREE STRUCTURE")
    print("="*60)
    db.show_table_structure("employees")
    
    print("\n" + "="*50)
    print("SELECT OPERATIONS (B-TREE SEARCH)")
    print("="*50)
    
    # Single record search
    db.select_record("employees", 150)
    db.select_record("employees", 999)  # Not found
    
    # Range search
    db.select_range("employees", 120, 200)
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    
    print("\nKey Points about B-Trees in SQL Databases:")
    print("• B-trees maintain sorted order for efficient range queries")
    print("• Tree remains balanced through node splitting")
    print("• Search complexity: O(log n)")
    print("• Ideal for disk-based storage (minimize disk reads)")
    print("• Each node can contain multiple keys (unlike binary trees)")

if __name__ == "__main__":
    main()