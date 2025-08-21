"""
Hash Generator Node for ComfyUI
Generates various types of hashes using seeds and base strings with configurable algorithms.
"""

# Standard library imports
import base64
import hashlib
import secrets
import time

class mbHashGenerator:
    """Generate hashes using various algorithms with seed and base string inputs."""
    
    # Class constants
    SUPPORTED_ALGORITHMS = ["sha1", "sha256", "sha512", "md5", "blake2b", "custom"]
    DEFAULT_ALGORITHM = "sha256"
    DEFAULT_SEED = "000000000000"
    DEFAULT_BASE_STRING = "text"
    
    # Character dictionary for custom hash encoding
    ENCODING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    # Custom hash configuration
    CUSTOM_HASH_LENGTH = 8
    CUSTOM_XOR_OFFSET = 8
    
    def __init__(self):
        """Initialize the hash generator node."""
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for hash generation."""
        return {
            "required": {
                "seed": ("STRING", {
                    "default": cls.DEFAULT_SEED,
                    "tooltip": "Seed value for hash generation (MAC address, UUID, or any string)"
                }),
                "base_string": ("STRING", {
                    "default": cls.DEFAULT_BASE_STRING,
                    "multiline": True,
                    "tooltip": "Base text to include in hash computation"
                }),
                "algorithm": (cls.SUPPORTED_ALGORITHMS, {
                    "default": cls.DEFAULT_ALGORITHM,
                    "tooltip": "Hash algorithm to use"
                }),
                "output_format": (["prefixed", "hash_only", "base64", "hex"], {
                    "default": "prefixed",
                    "tooltip": "Output format: prefixed (base-hash), hash only, base64, or hex"
                }),
                "include_timestamp": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Include current timestamp in hash computation for uniqueness"
                }),
            },
            "optional": {
                "salt": ("STRING", {
                    "default": "",
                    "tooltip": "Optional salt to add extra security to hash"
                }),
            }
        }

    # Node metadata
    TITLE = "Hash Generator"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("result", "hash_only", "algorithm_info")
    FUNCTION = "generate_hash"
    CATEGORY = "unset"
    DESCRIPTION = "Generate hashes using various algorithms (SHA1, SHA256, SHA512, MD5, BLAKE2b) with seeds and base strings."

    def generate_hash(self, seed, base_string, algorithm, output_format, include_timestamp, salt=""):
        """
        Generate hash using specified algorithm and parameters.
        
        Args:
            seed: Seed value for hash generation
            base_string: Base text to include in hash
            algorithm: Hash algorithm to use
            output_format: Format for output result
            include_timestamp: Whether to include timestamp
            salt: Optional salt for additional security
            
        Returns:
            tuple: (formatted_result, hash_only, algorithm_info)
        """
        try:
            # Prepare hash input data
            hash_input = self._prepare_hash_input(seed, base_string, salt, include_timestamp)
            
            # Generate hash based on algorithm
            if algorithm == "custom":
                hash_value = self._generate_custom_hash(hash_input, seed)
                algorithm_info = "Custom SHA1-based hash with XOR encoding"
            else:
                hash_value = self._generate_standard_hash(hash_input, algorithm)
                algorithm_info = f"{algorithm.upper()} hash algorithm"
            
            # Format output based on requested format
            formatted_result = self._format_output(base_string, hash_value, output_format)
            
            print(f"Generated {algorithm} hash for: {base_string[:50]}{'...' if len(base_string) > 50 else ''}")
            
            return (formatted_result, hash_value, algorithm_info)
            
        except Exception as e:
            error_msg = f"Hash generation failed: {str(e)}"
            print(error_msg)
            # Return safe fallback
            fallback_hash = hashlib.sha256(f"{seed}{base_string}".encode()).hexdigest()[:16]
            return (f"{base_string}-{fallback_hash}", fallback_hash, "Fallback SHA256")

    def _prepare_hash_input(self, seed, base_string, salt, include_timestamp):
        """Prepare the input data for hashing."""
        # Clean seed (remove colons, spaces, etc.)
        clean_seed = seed.replace(":", "").replace("-", "").replace(" ", "")
        
        # Build hash input components
        components = []
        
        # Add encoded components (maintaining compatibility with original)
        try:
            components.append(base64.b64decode("R2FyeQ==").decode("utf-8"))  # "Gary"
        except Exception:
            components.append("Gary")  # Fallback
        
        components.append(clean_seed)
        
        try:
            components.append(base64.b64decode("bWFzdGVy").decode("utf-8"))  # "master"
        except Exception:
            components.append("master")  # Fallback
        
        components.append(base_string)
        
        # Add optional salt
        if salt:
            components.append(salt)
        
        # Add timestamp if requested
        if include_timestamp:
            components.append(str(int(time.time())))
        
        return "".join(components)

    def _generate_standard_hash(self, hash_input, algorithm):
        """Generate hash using standard library algorithms."""
        input_bytes = hash_input.encode("utf-8")
        
        if algorithm == "sha1":
            return hashlib.sha1(input_bytes).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(input_bytes).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(input_bytes).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(input_bytes).hexdigest()
        elif algorithm == "blake2b":
            return hashlib.blake2b(input_bytes).hexdigest()
        else:
            # Fallback to SHA256
            return hashlib.sha256(input_bytes).hexdigest()

    def _generate_custom_hash(self, hash_input, seed):
        """Generate custom hash using original algorithm for compatibility."""
        try:
            # Use SHA1 for the base hash (original algorithm)
            md = hashlib.sha1(hash_input.encode("utf-8")).digest()
            
            # Apply XOR transformation (original algorithm)
            v = []
            for i in range(self.CUSTOM_HASH_LENGTH):
                k = i + self.CUSTOM_XOR_OFFSET + (i < 4) * self.CUSTOM_XOR_OFFSET
                if k < len(md):
                    v.append(md[i] ^ md[k])
                else:
                    # Fallback if digest is too short
                    v.append(md[i % len(md)])
            
            # Encode using character dictionary (original algorithm)
            encoded_chars = []
            for i in range(self.CUSTOM_HASH_LENGTH):
                char_index = v[i] + 2 * (v[i] // 62) - ((v[i] // 62) << 6)
                char_index = char_index % len(self.ENCODING_CHARS)
                encoded_chars.append(self.ENCODING_CHARS[char_index])
            
            return "".join(encoded_chars)
            
        except Exception as e:
            print(f"Custom hash generation failed: {str(e)}")
            # Fallback to simple hash
            return hashlib.sha1(hash_input.encode()).hexdigest()[:self.CUSTOM_HASH_LENGTH]

    def _format_output(self, base_string, hash_value, output_format):
        """Format the output based on the requested format."""
        if output_format == "prefixed":
            return f"{base_string}-{hash_value}"
        elif output_format == "hash_only":
            return hash_value
        elif output_format == "base64":
            try:
                return base64.b64encode(hash_value.encode()).decode()
            except Exception:
                return hash_value
        elif output_format == "hex":
            if all(c in "0123456789abcdefABCDEF" for c in hash_value):
                return hash_value.lower()
            else:
                # Convert to hex if not already
                return hash_value.encode().hex()
        else:
            # Default to prefixed
            return f"{base_string}-{hash_value}"

    @staticmethod
    def generate_secure_random_seed():
        """Generate a cryptographically secure random seed."""
        return secrets.token_hex(16)

    @staticmethod 
    def verify_hash(original_data, hash_value, algorithm="sha256"):
        """Verify if a hash matches the original data."""
        try:
            if algorithm == "custom":
                # Custom verification would need the original seed
                return False
            else:
                computed_hash = getattr(hashlib, algorithm)(original_data.encode()).hexdigest()
                return computed_hash == hash_value
        except Exception:
            return False
