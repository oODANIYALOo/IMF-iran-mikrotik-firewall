FROM archlinux
RUN pacman -Sy --noconfirm ansible python python-pip
RUN /bin/bash -c pip install paramiko
WORKDIR /app
COPY . .
