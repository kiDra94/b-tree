import time
import random
import statistics
import bisect

class BTreeNode:
    def __init__(self, leaf=False):
        self.keys = []
        self.values = []
        self.children = []
        self.leaf = leaf

class BTreeCorrected:
    def __init__(self, degree=50):
        self.root = BTreeNode(leaf=True)
        self.degree = degree
        self.search_comparisons = 0
        self.binary_searches = 0  # Track binary search operations
    
    def insert(self, key, value):
        """Insert without printing for performance"""
        root = self.root
        
        if len(root.keys) == (2 * self.degree) - 1:
            new_root = BTreeNode()
            self.root = new_root
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)
    
    def _insert_non_full(self, node, key, value):
        if node.leaf:
            # Use binary search to find insertion position
            pos = bisect.bisect_left(node.keys, key)
            node.keys.insert(pos, key)
            node.values.insert(pos, value)
        else:
            # Use binary search to find child to insert into
            pos = bisect.bisect_left(node.keys, key)
            
            if pos < len(node.keys) and node.keys[pos] == key:
                # Key already exists, update value
                node.values[pos] = value
                return
            
            if len(node.children[pos].keys) == (2 * self.degree) - 1:
                self._split_child(node, pos)
                if key > node.keys[pos]:
                    pos += 1
            
            self._insert_non_full(node.children[pos], key, value)
    
    def _split_child(self, parent, index):
        degree = self.degree
        full_child = parent.children[index]
        new_child = BTreeNode(leaf=full_child.leaf)
        
        mid_index = degree - 1
        mid_key = full_child.keys[mid_index]
        mid_value = full_child.values[mid_index]
        
        new_child.keys = full_child.keys[degree:]
        new_child.values = full_child.values[degree:]
        full_child.keys = full_child.keys[:mid_index]
        full_child.values = full_child.values[:mid_index]
        
        if not full_child.leaf:
            new_child.children = full_child.children[degree:]
            full_child.children = full_child.children[:degree]
        
        parent.children.insert(index + 1, new_child)
        parent.keys.insert(index, mid_key)
        parent.values.insert(index, mid_value)
    
    def search_with_stats(self, key):
        """Search using binary search and return timing + comparison statistics"""
        self.search_comparisons = 0
        self.binary_searches = 0
        start_time = time.perf_counter()
        
        result = self._search_node_binary(self.root, key)
        
        end_time = time.perf_counter()
        search_time = (end_time - start_time) * 1000000  # Convert to microseconds
        
        return result, search_time, self.search_comparisons, self.binary_searches
    
    def _search_node_binary(self, node, key):
        """Search using binary search within nodes"""
        self.binary_searches += 1
        
        # Use binary search to find position
        pos = bisect.bisect_left(node.keys, key)
        
        # Count the comparisons that bisect would make
        # Binary search makes approximately log2(n) comparisons
        if len(node.keys) > 0:
            import math
            self.search_comparisons += max(1, int(math.log2(len(node.keys)) + 1))
        
        # Check if key found at this position
        if pos < len(node.keys) and node.keys[pos] == key:
            return (node.keys[pos], node.values[pos])
        
        # If leaf node and key not found
        if node.leaf:
            return None
        
        # Recursively search appropriate child
        return self._search_node_binary(node.children[pos], key)
    

    
    def get_tree_stats(self):
        """Get statistics about the B-tree structure"""
        height = self._get_height(self.root)
        node_count = self._count_nodes(self.root)
        total_keys = self._count_keys(self.root)
        avg_keys_per_node = total_keys / node_count if node_count > 0 else 0
        
        return {
            'height': height,
            'nodes': node_count,
            'keys': total_keys,
            'degree': self.degree,
            'avg_keys_per_node': avg_keys_per_node
        }
    
    def _get_height(self, node):
        if node.leaf:
            return 1
        return 1 + max(self._get_height(child) for child in node.children)
    
    def _count_nodes(self, node):
        count = 1
        if not node.leaf:
            for child in node.children:
                count += self._count_nodes(child)
        return count
    
    def _count_keys(self, node):
        count = len(node.keys)
        if not node.leaf:
            for child in node.children:
                count += self._count_keys(child)
        return count

def linear_search(data_list, target):
    """Linear search for comparison"""
    comparisons = 0
    start_time = time.perf_counter()
    
    for key, value in data_list:
        comparisons += 1
        if key == target:
            end_time = time.perf_counter()
            return (key, value), (end_time - start_time) * 1000000, comparisons
    
    end_time = time.perf_counter()
    return None, (end_time - start_time) * 1000000, comparisons

def binary_search_list(data_list, target):
    """Binary search on sorted list for comparison"""
    comparisons = 0
    start_time = time.perf_counter()
    
    left, right = 0, len(data_list) - 1
    
    while left <= right:
        comparisons += 1
        mid = (left + right) // 2
        mid_key = data_list[mid][0]
        
        if mid_key == target:
            end_time = time.perf_counter()
            return data_list[mid], (end_time - start_time) * 1000000, comparisons
        elif mid_key < target:
            left = mid + 1
        else:
            right = mid - 1
    
    end_time = time.perf_counter()
    return None, (end_time - start_time) * 1000000, comparisons

def run_corrected_performance_test():
    print("="*80)
    print("B-TREE PERFORMANCE: LINEAR vs BINARY SEARCH COMPARISON")
    print("="*80)
    
    degrees = [10, 25, 50, 100, 500]
    num_records = 50000  # Smaller for detailed analysis
    
    print(f"Setting up test with {num_records:,} records...")
    
    # Generate test data
    test_data = [(i + 1000, f"Employee_{i + 1000}") for i in range(num_records)]
    random.shuffle(test_data)
    
    # Create sorted data for comparison searches
    sorted_data = sorted(test_data)
    
    print("\nBuilding B-trees...")
    btrees = {}
    
    for degree in degrees:
        print(f"  Building B-tree with degree {degree}...")
        btree = BTreeCorrected(degree)
        
        start_time = time.perf_counter()
        for key, value in test_data:
            btree.insert(key, value)
        end_time = time.perf_counter()
        
        btrees[degree] = btree
        stats = btree.get_tree_stats()
        print(f"    Height: {stats['height']}, Nodes: {stats['nodes']}, "
              f"Avg keys/node: {stats['avg_keys_per_node']:.1f}, Build time: {end_time-start_time:.3f}s")
    
    print("\n" + "="*80)
    print("SEARCH METHOD COMPARISON")
    print("="*80)
    
    # Test different search methods
    test_ids = random.sample(range(1000, 1000 + num_records), 1000)
    
    print("Running 1000 random searches with each method...\n")
    
    # 1. Linear search on unsorted list
    print("🔍 LINEAR SEARCH (unsorted list):")
    linear_times = []
    linear_comparisons = []
    
    for search_id in test_ids[:100]:  # Smaller sample for linear search
        result, time_taken, comparisons = linear_search(test_data, search_id)
        linear_times.append(time_taken)
        linear_comparisons.append(comparisons)
    
    print(f"   Average time: {statistics.mean(linear_times):.2f} μs")
    print(f"   Average comparisons: {statistics.mean(linear_comparisons):.1f}")
    print(f"   Max comparisons: {max(linear_comparisons)}")
    
    # 2. Binary search on sorted list
    print(f"\n🔍 BINARY SEARCH (sorted list):")
    binary_times = []
    binary_comparisons = []
    
    for search_id in test_ids:
        result, time_taken, comparisons = binary_search_list(sorted_data, search_id)
        binary_times.append(time_taken)
        binary_comparisons.append(comparisons)
    
    print(f"   Average time: {statistics.mean(binary_times):.2f} μs")
    print(f"   Average comparisons: {statistics.mean(binary_comparisons):.1f}")
    print(f"   Max comparisons: {max(binary_comparisons)}")
    
    # 3. B-tree with binary search
    print(f"\n🔍 B-TREE with BINARY SEARCH:")
    
    best_binary_degree = None
    best_binary_time = float('inf')
    
    for degree in degrees:
        btree = btrees[degree]
        times = []
        comparisons = []
        binary_searches = []
        
        for search_id in test_ids:
            result, time_taken, comps, bin_searches = btree.search_with_stats(search_id)
            times.append(time_taken)
            comparisons.append(comps)
            binary_searches.append(bin_searches)
        
        avg_time = statistics.mean(times)
        if avg_time < best_binary_time:
            best_binary_time = avg_time
            best_binary_degree = degree
        
        stats = btree.get_tree_stats()
        print(f"   Degree {degree:3d}: {avg_time:6.2f} μs, "
              f"{statistics.mean(comparisons):4.1f} comparisons avg, "
              f"{max(comparisons):2d} max, "
              f"{statistics.mean(binary_searches):3.1f} binary searches, "
              f"(avg {stats['avg_keys_per_node']:.1f} keys/node)")
    
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    
    print(f"\n📊 COMPARISON SUMMARY (average performance):")
    print(f"{'Method':<35} {'Time (μs)':<12} {'Comparisons':<12} {'Efficiency'}")
    print("-" * 75)
    
    linear_avg_time = statistics.mean(linear_times)
    linear_avg_comps = statistics.mean(linear_comparisons)
    binary_avg_time = statistics.mean(binary_times)
    binary_avg_comps = statistics.mean(binary_comparisons)
    
    print(f"{'Linear search (unsorted)':<35} {linear_avg_time:<12.2f} {linear_avg_comps:<12.1f} O(n)")
    print(f"{'Binary search (sorted list)':<35} {binary_avg_time:<12.2f} {binary_avg_comps:<12.1f} O(log n)")
    
    # Show B-tree results
    for degree in degrees:
        btree = btrees[degree]
        
        # Get binary search stats
        times_binary = []
        comps_binary = []
        for search_id in test_ids[:100]:  # Sample for comparison
            _, time_taken, comps, _ = btree.search_with_stats(search_id)
            times_binary.append(time_taken)
            comps_binary.append(comps)
        
        print(f"{'B-tree (d=' + str(degree) + ')':<35} {statistics.mean(times_binary):<12.2f} {statistics.mean(comps_binary):<12.1f} O(log n * log k)")
    
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"1. **Binary Search Within Nodes**: As B-tree degree increases, nodes get larger")
    print(f"2. **Efficiency Scales**: With degree 500, nodes can have ~1000 keys")
    print(f"   - Binary search in node: ~10 comparisons (log₂(1000))")
    print(f"3. **Overall Complexity**: O(log_d(n) * log(k)) where k = keys per node")
    print(f"4. **Real Impact**: With large degrees, binary search is essential")
    
    # Show degree impact
    print(f"\n📈 DEGREE IMPACT:")
    best_degree = min(degrees, key=lambda d: statistics.mean([
        btrees[d].search_with_stats(test_ids[i])[2] for i in range(10)
    ]))
    worst_degree = max(degrees, key=lambda d: statistics.mean([
        btrees[d].search_with_stats(test_ids[i])[2] for i in range(10)
    ]))
    
    best_stats = btrees[best_degree].get_tree_stats()
    worst_stats = btrees[worst_degree].get_tree_stats()
    
    print(f"Best performing degree: {best_degree} (height: {best_stats['height']}, avg keys/node: {best_stats['avg_keys_per_node']:.1f})")
    print(f"Highest degree tested: {worst_degree} (height: {worst_stats['height']}, avg keys/node: {worst_stats['avg_keys_per_node']:.1f})")
    
    print(f"\n📚 THEORETICAL ANALYSIS:")
    print(f"For a B-tree with n = {num_records:,} records and degree d:")
    print(f"• Tree height: O(log_d(n))")
    print(f"• Keys per node: up to 2d-1")
    print(f"• Binary search in node: O(log d)")
    print(f"• Total complexity: O(log_d(n) * log d)")
    print(f"\nWith large degrees (like databases use), binary search is essential!")
    
    print(f"\n💾 REAL DATABASE IMPACT:")
    print(f"Database systems like PostgreSQL and MySQL use degrees of 100-1000+")
    print(f"• With degree 1000: Binary search = ~11 comparisons per node")
    print(f"• With millions of records, efficient node search is crucial")
    print(f"• This is why real B-tree implementations always use binary search")

if __name__ == "__main__":
    run_corrected_performance_test()