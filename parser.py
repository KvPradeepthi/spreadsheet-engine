import re

class FormulaParser:
    def __init__(self):
        self.pos = 0
        self.text = ""
    
    def parse(self, formula):
        """Parse a formula and return cell dependencies"""
        if not formula or not isinstance(formula, str):
            return []
        
        if not formula.startswith('='):
            return []
        
        # Extract cell references using regex
        cell_pattern = r'\b([A-Z]+[0-9]+)\b'
        dependencies = re.findall(cell_pattern, formula[1:])
        return list(set(dependencies))  # Remove duplicates
    
    def evaluate_formula(self, formula, cell_values):
        """Evaluate a formula with given cell values"""
        if not formula or not isinstance(formula, str):
            return formula
        
        if not formula.startswith('='):
            return formula
        
        # Remove the '=' sign
        expression = formula[1:].strip()
        
        # Replace cell references with their values
        cell_pattern = r'\b([A-Z]+[0-9]+)\b'
        cells = re.findall(cell_pattern, expression)
        
        for cell in cells:
            if cell not in cell_values:
                return "#REF!"
            
            cell_val = cell_values[cell]
            
            # Check if the cell value is an error
            if isinstance(cell_val, str) and cell_val.startswith('#'):
                return cell_val  # Propagate error
            
            # Replace cell reference with its value
            expression = re.sub(r'\b' + cell + r'\b', str(cell_val), expression)
        
        # Evaluate the expression
        try:
            result = self._safe_eval(expression)
            return result
        except ZeroDivisionError:
            return "#DIV/0!"
        except Exception:
            return "#REF!"
    
    def _safe_eval(self, expression):
        """Safely evaluate mathematical expression"""
        # Remove spaces
        expression = expression.replace(' ', '')
        
        # Check for division by zero before eval
        if '/0' in expression.replace(' ', ''):
            raise ZeroDivisionError()
        
        # Only allow numbers, operators, and parentheses
        allowed_chars = set('0123456789+-*/().  ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Invalid characters in expression")
        
        # Evaluate using Python's eval (safe for numeric expressions)
        result = eval(expression)
        
        # Check if result is a division by zero
        if result == float('inf') or result == float('-inf'):
            raise ZeroDivisionError()
        
        return result
