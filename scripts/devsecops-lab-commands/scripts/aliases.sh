# DevSecOps & PortSwigger Web Security Academy Lab Aliases & Environment
# Automatically routes Burp-Parity Open-Source CLI stack through Caido (http://127.0.0.1:8080)

export SECLISTS="/usr/share/seclists"
export CAIDO_PROXY="http://127.0.0.1:8080"
export ZAP_PROXY="http://127.0.0.1:8081"
export LAB_CA_BUNDLE="/home/kali/.local/share/devsecops-lab/certs/caido-ca.pem"

# Browser & Proxy Chaining Controls
alias portswigger-browser='/usr/local/bin/portswigger-browser'
alias proxy-toggle='/usr/local/bin/proxy-toggle'
alias proxy-caido='/usr/local/bin/proxy-toggle caido'
alias proxy-zap='/usr/local/bin/proxy-toggle zap'
alias proxy-chain='/usr/local/bin/proxy-toggle chain'
alias proxy-direct='/usr/local/bin/proxy-toggle direct'
alias proxy-status='/usr/local/bin/proxy-toggle status'

# 1. Fuzzing (Replaces unthrottled Burp Intruder): ffuf + SecLists
alias ffuf-caido='ffuf -x http://127.0.0.1:8080'
alias ffuf-replay='ffuf -replay-proxy http://127.0.0.1:8080'

# 2. Active Vulnerability Scanning (Replaces Burp Pro Scanner): nuclei
alias nuclei-caido='nuclei -proxy http://127.0.0.1:8080'

# 3. Out-of-Band OAST (Replaces Burp Collaborator): interactsh-client
alias interactsh-caido='HTTP_PROXY=http://127.0.0.1:8080 HTTPS_PROXY=http://127.0.0.1:8080 /usr/local/bin/interactsh-client'

# 4. Modern JS/Headless Crawling (Replaces Burp Crawler): katana + httpx
alias katana-caido='katana -proxy http://127.0.0.1:8080'
alias httpx-caido='/usr/local/bin/httpx -proxy http://127.0.0.1:8080'

# 5. SQLi & Parameter Discovery: sqlmap + arjun
alias sqlmap-caido='sqlmap --proxy="http://127.0.0.1:8080"'
alias arjun-caido='PYTHONWARNINGS="ignore:Unverified HTTPS request" HTTP_PROXY=http://127.0.0.1:8080 HTTPS_PROXY=http://127.0.0.1:8080 arjun -oB 127.0.0.1:8080'
