"""
Python Expression Evaluator Node for ComfyUI
Evaluates Python expressions on inputs with safe execution environment.
"""

# Local imports
from .common import any_typ

class mbEval:
    """Evaluate Python expressions on inputs and return the result."""
    
    # Class constants
    DEFAULT_CODE = "i1"
    FALLBACK_CODE = "i1"
    
    # Safe built-ins for expression evaluation
    SAFE_BUILTINS = {
        '__builtins__': {
            'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
            'chr': chr, 'dict': dict, 'enumerate': enumerate, 'filter': filter,
            'float': float, 'hex': hex, 'int': int, 'len': len, 'list': list,
            'map': map, 'max': max, 'min': min, 'oct': oct, 'ord': ord,
            'pow': pow, 'range': range, 'round': round, 'set': set,
            'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple,
            'zip': zip
        }
    }
    
    def __init__(self):
        """Initialize the Python expression evaluator node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for Python expression evaluation."""
        return {
            "required": {
                "code": ("STRING", {
                    "default": cls.DEFAULT_CODE,
                    "multiline": True,
                    "tooltip": "Python expression to evaluate (e.g., 'i1 + i2', 'len(i1)', 'max(i1, i2)')"
                }),
            },
            "optional": {
                "i1": (any_typ, {
                    "tooltip": "First input variable (accessible as 'i1' in expression)"
                }),
            }
        }

    # Node metadata
    TITLE = "Python Expression Evaluator"
    RETURN_TYPES = (any_typ, "STRING")
    RETURN_NAMES = ("result", "error")
    FUNCTION = "evaluate_expression"
    CATEGORY = "unset"
    DESCRIPTION = "Evaluate Python expressions on inputs with access to safe built-in functions and mathematical operations. Returns error message if evaluation fails."

    def evaluate_expression(self, code, **kwargs):
        """
        Evaluate Python expression with input variables.
        
        Args:
            code: Python expression to evaluate
            **kwargs: Variable number of input variables (i1, i2, etc.)
            
        Returns:
            tuple: (Result of expression evaluation, Error message or None)
        """
        try:
            # Prepare execution environment
            execution_env = self._prepare_execution_environment(kwargs)
            
            # Validate and prepare code
            expression_code = self._prepare_expression_code(code)
            
            # Evaluate expression safely
            result = self._safe_evaluate(expression_code, execution_env)
            
            return (result, None)
            
        except Exception as e:
            error_msg = f"Expression evaluation failed: {str(e)}"
            print(error_msg)
            # Return first available input as fallback with error message
            fallback_result = self._get_fallback_result(kwargs)
            return (fallback_result[0], error_msg)

    def _prepare_execution_environment(self, input_vars):
        """Prepare safe execution environment with input variables."""
        # Create execution environment with safe builtins
        execution_env = self.SAFE_BUILTINS.copy()
        
        # Add input variables to environment
        for key, value in input_vars.items():
            execution_env[key] = value
        
        # Add common mathematical functions
        import math
        math_functions = {
            'math': math,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
            'pi': math.pi, 'e': math.e
        }
        execution_env.update(math_functions)
        
        return execution_env

    def _prepare_expression_code(self, code):
        """Prepare and validate expression code."""
        # Use fallback if code is empty
        if not code or code.strip() == "":
            return self.FALLBACK_CODE
        
        # Basic validation - check for dangerous keywords
        dangerous_keywords = ['import', 'exec', 'eval', 'open', 'file', '__']
        code_lower = code.lower()
        
        for keyword in dangerous_keywords:
            if keyword in code_lower:
                print(f"Warning: Potentially unsafe keyword '{keyword}' in expression")
        
        return code.strip()

    def _safe_evaluate(self, expression, environment):
        """Safely evaluate expression in controlled environment."""
        try:
            # Use eval in controlled environment
            result = eval(expression, {"__builtins__": environment['__builtins__']}, environment)
            return result
        except NameError as e:
            raise ValueError(f"Undefined variable in expression: {str(e)}")
        except SyntaxError as e:
            raise ValueError(f"Invalid syntax in expression: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Evaluation error: {str(e)}")

    def _get_fallback_result(self, input_vars):
        """Get fallback result when evaluation fails."""
        # Return first available input, or None if no inputs
        for key, value in input_vars.items():
            if value is not None:
                return (value,)
        return (None,)

