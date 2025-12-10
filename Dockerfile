FROM alpine:latest

# install dependencys package in image
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

# add path for ansible and ...
ENV PATH="/root/.local/bin:${PATH}"

# install ansible and dependencys
RUN python3 -m pip install --break-system-packages --user paramiko ansible-pylibssh ansible-core==2.20.0
# install ansible collection requirements
RUN ansible-galaxy collection install ansible.netcommon ansible.posix ansible.utils community.routeros
# install requerment for web and django
COPY web/requerment.txt /app/web/requerment.txt
RUN pip install --break-system-packages -r /app/web/requerment.txt
EXPOSE 8000
ENV PATH="/app/script/:${PATH}"

# for config ansible
COPY ansible.cfg /etc/ansible/

WORKDIR /app
COPY . .

CMD ["/bin/bash", "./main.sh"]
