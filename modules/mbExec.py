"""
Python Code Executor Node for ComfyUI
Executes Python code with inputs and returns the result through 'out' variable.
"""

# Local imports
from .common import any_typ, CATEGORIES


class mbExec:
    """Execute Python code on inputs and return the result via 'out' variable."""
    
    # Class constants
    DEFAULT_CODE = "out = i1"
    FALLBACK_CODE = "out = i1"
    HIDDEN_MARKER = "# __HIDDEN__"
    OUTPUT_VARIABLE = "out"
    
    # Safe built-ins for code execution
    SAFE_BUILTINS = {
        '__builtins__': {
            'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
            'chr': chr, 'dict': dict, 'enumerate': enumerate, 'filter': filter,
            'float': float, 'hex': hex, 'int': int, 'len': len, 'list': list,
            'map': map, 'max': max, 'min': min, 'oct': oct, 'ord': ord,
            'pow': pow, 'range': range, 'round': round, 'set': set,
            'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple,
            'zip': zip, 'print': print
        }
    }
    
    def __init__(self):
        """Initialize the Python code executor node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for Python code execution."""
        return {
            "required": {
                "code": ("STRING", {
                    "default": cls.DEFAULT_CODE,
                    "multiline": True,
                    "tooltip": "Python code to execute. Set 'out' variable to return result (e.g., 'out = i1 + i2')"
                }),
            },
            "optional": {
                "i1": (any_typ, {
                    "tooltip": "First input variable (accessible as 'i1' in code)"
                }),
            }
        }

    # Node metadata
    TITLE = "Python Code Executor"
    RETURN_TYPES = (any_typ, "STRING")
    RETURN_NAMES = ("out", "error")
    FUNCTION = "execute_code"
    CATEGORY = "unset"
    DESCRIPTION = "Execute Python code on inputs with access to safe built-in functions. Set 'out' variable to return result. Returns error message if execution fails."

    def execute_code(self, code, **kwargs):
        """
        Execute Python code with input variables.
        
        Args:
            code: Python code to execute
            **kwargs: Variable number of input variables (i1, i2, etc.)
            
        Returns:
            tuple: (Value of 'out' variable after code execution, Error message or None)
        """
        try:
            # Prepare execution environment
            globals_env, locals_env = self._prepare_execution_environment(kwargs)
            
            # Validate and prepare code
            execution_code = self._prepare_execution_code(code)
            
            # Execute code safely
            result = self._safe_execute(execution_code, globals_env, locals_env)
            
            return (result, None)
            
        except Exception as e:
            error_msg = f"Code execution failed: {str(e)}"
            print(error_msg)
            # Return first available input as fallback with error message
            fallback_result = self._get_fallback_result(kwargs)
            return (fallback_result[0], error_msg)

    def _prepare_execution_environment(self, input_vars):
        """Prepare safe execution environment with input variables."""
        # Create global environment with safe builtins
        globals_env = self.SAFE_BUILTINS.copy()
        
        # Add input variables to global environment
        for key, value in input_vars.items():
            globals_env[key] = value
        
        # Add common mathematical functions
        import math
        math_functions = {
            'math': math,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
            'pi': math.pi, 'e': math.e
        }
        globals_env.update(math_functions)
        
        # Create local environment for execution
        locals_env = {}
        
        return globals_env, locals_env

    def _prepare_execution_code(self, code):
        """Prepare and validate execution code."""
        # Remove hidden marker if present
        cleaned_code = self._remove_hidden_marker(code)
        
        # Use fallback if code is empty
        if not cleaned_code or cleaned_code.strip() == "":
            return self.FALLBACK_CODE
        
        # Basic validation - check for dangerous keywords
        self._validate_code_safety(cleaned_code)
        
        return cleaned_code.strip()

    def _remove_hidden_marker(self, code):
        """Remove hidden marker from code if present."""
        if code.startswith(self.HIDDEN_MARKER):
            lines = code.split('\n')
            if len(lines) > 1:
                return '\n'.join(lines[1:])  # Remove first line
            else:
                return ""  # Only the marker was present
        return code

    def _validate_code_safety(self, code):
        """Validate code for basic safety (warning only)."""
        dangerous_keywords = ['import', '__import__', 'exec', 'eval', 'open', 'file', 'globals', '__']
        code_lower = code.lower()
        
        for keyword in dangerous_keywords:
            if keyword in code_lower:
                print(f"Warning: Potentially unsafe keyword '{keyword}' in code")

    def _safe_execute(self, code, globals_env, locals_env):
        """Safely execute code in controlled environment."""
        try:
            # Execute code in controlled environment
            exec(code, globals_env, locals_env)
            
            # Extract output variable
            if self.OUTPUT_VARIABLE in locals_env:
                return locals_env[self.OUTPUT_VARIABLE]
            else:
                print(f"Warning: '{self.OUTPUT_VARIABLE}' variable not set in code")
                return None
                
        except NameError as e:
            raise ValueError(f"Undefined variable in code: {str(e)}")
        except SyntaxError as e:
            raise ValueError(f"Invalid syntax in code: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Execution error: {str(e)}")

    def _get_fallback_result(self, input_vars):
        """Get fallback result when execution fails."""
        # Return first available input, or None if no inputs
        for key, value in input_vars.items():
            if value is not None:
                return (value,)
        return (None,)
