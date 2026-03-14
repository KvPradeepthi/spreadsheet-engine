class Evaluator:
    def __init__(self, parser, graph_manager):
        self.parser = parser
        self.graph_manager = graph_manager
    
    def recalculate(self, sheet_id, sheets, graph_manager):
        """Recalculate all cells in the sheet that need updating"""
        if sheet_id not in sheets:
            return
        
        # Get all cells in the sheet
        all_cells = list(sheets[sheet_id].keys())
        
        # Get cells in topological order
        sorted_cells = graph_manager.topological_sort(sheet_id, all_cells)
        
        # Recalculate each cell
        for cell_id in sorted_cells:
            cell_value = sheets[sheet_id].get(cell_id)
            
            # Skip if it's already an error (like #CYCLE!)
            if isinstance(cell_value, str) and cell_value == "#CYCLE!":
                continue
            
            # If it's a formula, evaluate it
            if isinstance(cell_value, str) and cell_value.startswith('='):
                evaluated_value = self._evaluate_cell(sheet_id, cell_id, sheets)
                sheets[sheet_id][cell_id] = evaluated_value
    
    def _evaluate_cell(self, sheet_id, cell_id, sheets):
        """Evaluate a single cell's formula"""
        cell_value = sheets[sheet_id].get(cell_id)
        
        # If it's not a formula, return as is
        if not isinstance(cell_value, str) or not cell_value.startswith('='):
            return cell_value
        
        # Check if it's already evaluated to an error
        if cell_value.startswith('#'):
            return cell_value
        
        # Get all cell values for evaluation
        cell_values = {}
        
        # Extract dependencies
        dependencies = self.parser.parse(cell_value)
        
        # Build cell_values dictionary with current values
        for dep_cell in dependencies:
            if dep_cell in sheets[sheet_id]:
                dep_value = sheets[sheet_id][dep_cell]
                
                # If dependency is a formula, evaluate it first
                if isinstance(dep_value, str) and dep_value.startswith('='):
                    dep_value = self._evaluate_cell(sheet_id, dep_cell, sheets)
                    sheets[sheet_id][dep_cell] = dep_value
                
                cell_values[dep_cell] = dep_value
            else:
                # Cell doesn't exist
                cell_values[dep_cell] = None
        
        # Evaluate the formula
        result = self.parser.evaluate_formula(cell_value, cell_values)
        
        return result
