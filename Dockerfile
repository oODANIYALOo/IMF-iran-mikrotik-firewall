FROM alpine:latest

RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    openssh-client \
    sshpass \
    git \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    make dialog bash libssh-dev

ENV PATH="/root/.local/bin:${PATH}"
RUN python3 -m pip install --break-system-packages --user paramiko ansible-pylibssh ansible-core==2.20.0


RUN ansible-galaxy collection install ansible.netcommon ansible.posix ansible.utils community.routeros

COPY ansible.cfg /etc/ansible/

WORKDIR /app
COPY . .

CMD ["/bin/bash"]
