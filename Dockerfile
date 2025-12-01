FROM archlinux
RUN pacman -Sy --noconfirm ansible python python-pip dialog gcc
RUN pacman -Sy --noconfirm libssh libssh2
RUN /bin/bash -c "pip install --break-system-packages paramiko ansible-pylibssh"
WORKDIR /app
COPY . .
