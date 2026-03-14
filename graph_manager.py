class GraphManager:
    def __init__(self):
        # adjacency list: {sheet_id: {cell: [dependents]}}
        self.dependencies = {}
        # reverse graph: {sheet_id: {cell: [dependencies]}}
        self.reverse_dependencies = {}
    
    def update_dependencies(self, sheet_id, cell_id, value, sheets):
        """Update the dependency graph when a cell is updated"""
        from parser import FormulaParser
        
        if sheet_id not in self.dependencies:
            self.dependencies[sheet_id] = {}
            self.reverse_dependencies[sheet_id] = {}
        
        # Remove old dependencies for this cell
        if cell_id in self.reverse_dependencies[sheet_id]:
            old_deps = self.reverse_dependencies[sheet_id][cell_id]
            for dep in old_deps:
                if dep in self.dependencies[sheet_id]:
                    if cell_id in self.dependencies[sheet_id][dep]:
                        self.dependencies[sheet_id][dep].remove(cell_id)
            self.reverse_dependencies[sheet_id][cell_id] = []
        
        # If the value is a formula, extract dependencies
        if isinstance(value, str) and value.startswith('='):
            parser = FormulaParser()
            deps = parser.parse(value)
            
            # Check for cycles before adding
            self.reverse_dependencies[sheet_id][cell_id] = deps
            
            # Temporarily add edges to check for cycles
            for dep in deps:
                if dep not in self.dependencies[sheet_id]:
                    self.dependencies[sheet_id][dep] = []
                self.dependencies[sheet_id][dep].append(cell_id)
            
            # Check for cycles
            if self._has_cycle(sheet_id, cell_id):
                # Remove the edges we just added
                for dep in deps:
                    if cell_id in self.dependencies[sheet_id][dep]:
                        self.dependencies[sheet_id][dep].remove(cell_id)
                self.reverse_dependencies[sheet_id][cell_id] = []
                
                # Mark all cells in the cycle with #CYCLE! error
                self._mark_cycle_error(sheet_id, cell_id, sheets)
        else:
            # If it's not a formula, clear dependencies
            self.reverse_dependencies[sheet_id][cell_id] = []
    
    def _has_cycle(self, sheet_id, start_cell):
        """Check if there's a cycle starting from start_cell using DFS"""
        visited = set()
        rec_stack = set()
        
        def dfs(cell):
            visited.add(cell)
            rec_stack.add(cell)
            
            if cell in self.dependencies.get(sheet_id, {}):
                for neighbor in self.dependencies[sheet_id][cell]:
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(cell)
            return False
        
        return dfs(start_cell)
    
    def _mark_cycle_error(self, sheet_id, cell_id, sheets):
        """Mark all cells in the cycle with #CYCLE! error"""
        # Find all cells in the cycle using DFS
        cycle_cells = self._find_cycle_cells(sheet_id, cell_id)
        
        # Mark all cells in the cycle with error
        for cell in cycle_cells:
            if cell in sheets[sheet_id]:
                sheets[sheet_id][cell] = "#CYCLE!"
    
    def _find_cycle_cells(self, sheet_id, start_cell):
        """Find all cells involved in the cycle"""
        visited = set()
        rec_stack = set()
        cycle_cells = set()
        
        def dfs(cell, path):
            visited.add(cell)
            rec_stack.add(cell)
            path.append(cell)
            
            if cell in self.dependencies.get(sheet_id, {}):
                for neighbor in self.dependencies[sheet_id][cell]:
                    if neighbor not in visited:
                        dfs(neighbor, path)
                    elif neighbor in rec_stack:
                        # Found a cycle, add all cells from neighbor to end of path
                        idx = path.index(neighbor)
                        cycle_cells.update(path[idx:])
            
            rec_stack.remove(cell)
            path.pop()
        
        dfs(start_cell, [])
        return cycle_cells if cycle_cells else {start_cell}
    
    def get_dependents(self, sheet_id, cell_id):
        """Get all cells that depend on the given cell"""
        if sheet_id not in self.dependencies:
            return []
        return self.dependencies[sheet_id].get(cell_id, [])
    
    def topological_sort(self, sheet_id, cells):
        """Return cells in topological order for recalculation"""
        if sheet_id not in self.reverse_dependencies:
            return cells
        
        in_degree = {}
        for cell in cells:
            in_degree[cell] = len(self.reverse_dependencies[sheet_id].get(cell, []))
        
        queue = [cell for cell in cells if in_degree[cell] == 0]
        result = []
        
        while queue:
            cell = queue.pop(0)
            result.append(cell)
            
            for dependent in self.get_dependents(sheet_id, cell):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        return result
