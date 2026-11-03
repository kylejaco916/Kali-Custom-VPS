# PASTE THIS 5-LINE CELL INTO GOOGLE COLAB (REPLACES ALL NOTEBOOK CODE)
!curl -fsSL https://tailscale.com/install.sh | sh && apt-get update -qq && apt-get install -y -qq openssh-server zstd psmisc > /dev/null
!mkdir -p /var/run/sshd /root/.ssh && chmod 700 /root/.ssh && echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICvYi1P8BDQay1/1T712BpWjb8gIAMhw0GqKMC4E5Rda kali-to-termux" > /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys
!ssh-keygen -A >/dev/null 2>&1 && sed -i 's/#\?Port .*/Port 2222/' /etc/ssh/sshd_config && grep -q '^PermitRootLogin' /etc/ssh/sshd_config || echo -e "PermitRootLogin prohibit-password\nPubkeyAuthentication yes" >> /etc/ssh/sshd_config && (killall -q sshd || true) && /usr/sbin/sshd
!killall -q tailscaled || true; nohup tailscaled --tun=userspace-networking --socks5-server=localhost:1055 > /tmp/tailscaled.log 2>&1 &
!sleep 3 && tailscale up --hostname="colab-gpu" --accept-routes
