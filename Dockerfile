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
    make

RUN python3 -m pip install --break-system-packages --user pipx
ENV PATH="/root/.local/bin:${PATH}"
RUN python3 -m pipx ensurepath

RUN pipx install ansible-core

RUN apk install dialog

WORKDIR /app
COPY . .

CMD ["/bin/sh"]
