import time
import random
import statistics

class BTreeNode:
    def __init__(self, leaf=False):
        self.keys = []
        self.values = []
        self.children = []
        self.leaf = leaf

class BTreePerformance:
    def __init__(self, degree=50):  # Higher degree for better performance with large datasets
        self.root = BTreeNode(leaf=True)
        self.degree = degree
        self.total_nodes = 0
        self.search_comparisons = 0
    
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
        i = len(node.keys) - 1
        
        if node.leaf:
            node.keys.append(None)
            node.values.append(None)
            
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if len(node.children[i].keys) == (2 * self.degree) - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key, value)
    
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
        """Search and return timing + comparison statistics"""
        self.search_comparisons = 0
        start_time = time.perf_counter()
        
        result = self._search_node(self.root, key)
        
        end_time = time.perf_counter()
        search_time = (end_time - start_time) * 1000000  # Convert to microseconds
        
        return result, search_time, self.search_comparisons
    
    def _search_node(self, node, key):
        """Search with comparison counting"""
        i = 0
        
        while i < len(node.keys):
            self.search_comparisons += 1
            if key == node.keys[i]:
                return (node.keys[i], node.values[i])
            elif key < node.keys[i]:
                break
            i += 1
        
        if node.leaf:
            return None
        
        return self._search_node(node.children[i], key)
    
    def get_tree_stats(self):
        """Get statistics about the B-tree structure"""
        height = self._get_height(self.root)
        node_count = self._count_nodes(self.root)
        total_keys = self._count_keys(self.root)
        
        return {
            'height': height,
            'nodes': node_count,
            'keys': total_keys,
            'degree': self.degree
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

def run_performance_test():
    print("="*70)
    print("B-TREE SEARCH PERFORMANCE ANALYZER")
    print("="*70)
    
    # Create B-tree with different degrees for comparison
    degrees = [5, 10, 25, 50, 100, 1000]
    num_records = 100000
    
    print(f"Setting up B-trees with {num_records:,} records...")
    
    # Generate test data
    print("Generating random employee data...")
    test_data = []
    for i in range(num_records):
        emp_id = i + 1000  # IDs from 1000 to 10999
        name = f"Employee_{emp_id}"
        test_data.append((emp_id, name))
    
    # Shuffle for realistic insertion order
    random.shuffle(test_data)
    
    # Create B-trees with different degrees
    btrees = {}
    for degree in degrees:
        print(f"Building B-tree with degree {degree}...")
        btree = BTreePerformance(degree)
        
        start_time = time.perf_counter()
        for key, value in test_data:
            btree.insert(key, value)
        end_time = time.perf_counter()
        
        btrees[degree] = btree
        stats = btree.get_tree_stats()
        
        print(f"  Degree {degree}: Height={stats['height']}, Nodes={stats['nodes']}, Build time={end_time-start_time:.3f}s")
    
    # Create linear search data for comparison
    sorted_data = sorted(test_data)
    
    print("\n" + "="*70)
    print("SEARCH PERFORMANCE COMPARISON")
    print("="*70)
    
    while True:
        try:
            print(f"\nEnter employee ID to search (1000-{999+num_records}) or 'quit' to exit:")
            user_input = input("ID: ").strip()
            
            if user_input.lower() == 'quit':
                break
            
            search_id = int(user_input)
            
            if search_id < 1000 or search_id >= 1000 + num_records:
                print(f"ID must be between 1000 and {999+num_records}")
                continue
            
            print(f"\n🔍 Searching for Employee ID: {search_id}")
            print("-" * 50)
            
            # Test linear search
            linear_result, linear_time, linear_comps = linear_search(sorted_data, search_id)
            
            print(f"📊 LINEAR SEARCH:")
            if linear_result:
                print(f"   ✅ Found: {linear_result[1]}")
            else:
                print(f"   ❌ Not found")
            print(f"   ⏱️  Time: {linear_time:.2f} μs")
            print(f"   🔢 Comparisons: {linear_comps:,}")
            
            print()
            
            # Test B-tree searches
            print(f"📊 B-TREE SEARCHES:")
            best_time = float('inf')
            best_degree = None
            
            for degree in degrees:
                btree = btrees[degree]
                result, search_time, comparisons = btree.search_with_stats(search_id)
                
                if search_time < best_time:
                    best_time = search_time
                    best_degree = degree
                
                print(f"   Degree {degree:3d}: ", end="")
                if result:
                    print(f"✅ Found | Time: {search_time:6.2f} μs | Comparisons: {comparisons:2d}")
                else:
                    print(f"❌ Not found | Time: {search_time:6.2f} μs | Comparisons: {comparisons:2d}")
            
            print(f"\n🏆 PERFORMANCE SUMMARY:")
            print(f"   Best B-tree (degree {best_degree}): {best_time:.2f} μs")
            print(f"   Linear search: {linear_time:.2f} μs")
            if linear_time > best_time:
                speedup = linear_time / best_time
                print(f"   🚀 B-tree is {speedup:.1f}x FASTER than linear search!")
            else:
                print(f"   📈 Linear search was faster (small dataset effect)")
            
            print(f"   💡 Comparison reduction: {linear_comps:,} → {btrees[best_degree].search_comparisons} comparisons")
            
        except ValueError:
            print("Please enter a valid number or 'quit'")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
    
    # Run automated benchmark
    print("\n" + "="*70)
    print("AUTOMATED BENCHMARK - RANDOM SEARCHES")
    print("="*70)
    
    # Test with random searches
    random_ids = random.sample(range(1000, 1000 + num_records), 100)
    
    print("Running 100 random searches...")
    
    # Linear search benchmark
    linear_times = []
    linear_comparisons = []
    
    for search_id in random_ids:
        _, time_taken, comparisons = linear_search(sorted_data, search_id)
        linear_times.append(time_taken)
        linear_comparisons.append(comparisons)
    
    # B-tree benchmarks
    btree_results = {}
    for degree in degrees:
        btree = btrees[degree]
        times = []
        comparisons = []
        
        for search_id in random_ids:
            _, time_taken, comps = btree.search_with_stats(search_id)
            times.append(time_taken)
            comparisons.append(comps)
        
        btree_results[degree] = {
            'times': times,
            'comparisons': comparisons
        }
    
    # Print benchmark results
    print(f"\n📈 BENCHMARK RESULTS (100 searches):")
    print(f"{'Method':<15} {'Avg Time (μs)':<15} {'Avg Comparisons':<18} {'Max Comparisons':<18}")
    print("-" * 70)
    
    print(f"{'Linear Search':<15} {statistics.mean(linear_times):<15.2f} {statistics.mean(linear_comparisons):<18.1f} {max(linear_comparisons):<18}")
    
    for degree in degrees:
        avg_time = statistics.mean(btree_results[degree]['times'])
        avg_comps = statistics.mean(btree_results[degree]['comparisons'])
        max_comps = max(btree_results[degree]['comparisons'])
        
        print(f"{'B-tree (d=' + str(degree) + ')':<15} {avg_time:<15.2f} {avg_comps:<18.1f} {max_comps:<18}")
    
    print("\n💡 Key Insights:")
    print("• B-trees show consistent O(log n) performance")
    print("• Higher degree = shorter tree = fewer comparisons")
    print("• Linear search: O(n) - performance degrades with data size")
    print("• B-trees excel with large datasets (database-scale)")
    
    # Add detailed explanation of B-tree degree
    print("\n" + "="*70)
    print("UNDERSTANDING B-TREE DEGREE")
    print("="*70)
    
    print("\n🎯 What is B-Tree Degree?")
    print("The 'degree' (also called 't' or minimum degree) is a parameter that defines:")
    print("• How many keys each node can hold")
    print("• How wide vs tall the tree becomes")
    print("• The tree's search performance characteristics")
    
    print(f"\n📏 Degree Rules:")
    print("For a B-tree with degree 't':")
    print("• Minimum keys per node: t - 1 (except root)")
    print("• Maximum keys per node: 2t - 1")
    print("• Maximum children per node: 2t")
    
    print(f"\n📊 Our Test Results Explained:")
    for degree in degrees:
        min_keys = degree - 1
        max_keys = 2 * degree - 1
        max_children = 2 * degree
        stats = btrees[degree].get_tree_stats()
        
        print(f"   Degree {degree:3d}: Max {max_keys:2d} keys/node → Tree height: {stats['height']} → Avg {statistics.mean(btree_results[degree]['comparisons']):.1f} comparisons")
    
    print(f"\n🌳 Tree Structure Impact:")
    print("Lower Degree (e.g., 10):")
    print("  ✓ Smaller nodes, easier to split")
    print("  ✗ Taller tree, more levels to search")
    print()
    print("Higher Degree (e.g., 100):")
    print("  ✓ Wider nodes, shorter tree")
    print("  ✓ Fewer levels to traverse")
    print("  ✗ More keys to scan within each node")
    
    print(f"\n💾 Real Database Examples:")
    print("• MySQL InnoDB: ~1000-2000 (fits 16KB disk pages)")
    print("• PostgreSQL: ~300-500 (fits 8KB disk pages)")
    print("• Our demo: 10-100 (for educational purposes)")
    
    print(f"\n🔑 Why Higher Degree Often Wins:")
    print("• Fewer tree levels = fewer disk reads")
    print("• Scanning keys within a node is fast (memory operation)")
    print("• Disk I/O is ~1000x slower than memory access")
    print("• Better cache utilization")
    
    print(f"\n🎯 Optimal Degree Selection:")
    print("Real databases choose degree based on:")
    print("• Disk page size (4KB, 8KB, 16KB)")
    print("• Average key + value size")
    print("• Cache line size (typically 64 bytes)")
    print("• Goal: Maximize keys per disk page")
    
    print(f"\n📈 Performance Summary from Our Test:")
    best_degree = min(degrees, key=lambda d: statistics.mean(btree_results[d]['comparisons']))
    worst_degree = max(degrees, key=lambda d: statistics.mean(btree_results[d]['comparisons']))
    
    print(f"• Best performing degree: {best_degree} ({statistics.mean(btree_results[best_degree]['comparisons']):.1f} avg comparisons)")
    print(f"• Worst performing degree: {worst_degree} ({statistics.mean(btree_results[worst_degree]['comparisons']):.1f} avg comparisons)")
    print(f"• Performance improvement: {statistics.mean(btree_results[worst_degree]['comparisons'])/statistics.mean(btree_results[best_degree]['comparisons']):.1f}x better")
    
    print(f"\n🧠 Remember: In real databases with millions/billions of records,")
    print(f"    the degree choice can mean the difference between 3 vs 15 disk reads!")
    print("    That's why B-tree degree optimization is crucial for database performance.")

if __name__ == "__main__":
    run_performance_test()