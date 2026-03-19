$port = 8080
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
$listener.Start()

Write-Host "Listening on http://127.0.0.1:$port"

try {
    while($true) {
        if (!$listener.Pending()) { Start-Sleep -Milliseconds 100; continue }
        $client = $listener.AcceptTcpClient()
        $stream = $client.GetStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $writer = New-Object System.IO.StreamWriter($stream)
        
        $request = $reader.ReadLine()
        while($reader.ReadLine() -ne "") {} # consume headers
        
        if ($request -match "^GET (\/\S*) HTTP") {
            $path = $matches[1].Replace('/', '\').TrimStart('\')
            if ($path -eq '' -or $path -eq '?') { $path = 'index.html' }
            
            # Basic security - prevent directory traversal
            $path = $path.Replace('..', '')
            $fullPath = Join-Path (Get-Location) $path
            
            if (Test-Path $fullPath -PathType Leaf) {
                $bytes = [System.IO.File]::ReadAllBytes($fullPath)
                if ($path -match "\.css$") { $contentType = "text/css" }
                elseif ($path -match "\.js$") { $contentType = "application/javascript" }
                elseif ($path -match "\.png$") { $contentType = "image/png" }
                elseif ($path -match "\.jpg$") { $contentType = "image/jpeg" }
                else { $contentType = "text/html" }
                
                $writer.WriteLine("HTTP/1.1 200 OK")
                $writer.WriteLine("Content-Type: $contentType")
                $writer.WriteLine("Content-Length: $($bytes.Length)")
                $writer.WriteLine("Connection: close")
                $writer.WriteLine("")
                $writer.Flush()
                $stream.Write($bytes, 0, $bytes.Length)
            } else {
                $writer.WriteLine("HTTP/1.1 404 Not Found`r`nConnection: close`r`n`r`n404 Not Found")
                $writer.Flush()
            }
        }
        $client.Close()
    }
} finally {
    $listener.Stop()
}
