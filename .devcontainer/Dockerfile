FROM mcr.microsoft.com/devcontainers/miniconda:0-3 AS base

ARG UNAME=vscode
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG GITHUB_TOKEN

USER root
# RUN groupmod -g $GROUP_ID $UNAME
# RUN usermod -u $USER_ID -g $GROUP_ID $UNAME

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends poppler-utils ffmpeg libsm6 libxext6

RUN mkdir -p /tmp/pip-tmp && chown -R $USER_ID:$GROUP_ID /tmp/pip-tmp
RUN mkdir -p /tmp/conda-tmp && chown -R $USER_ID:$GROUP_ID /tmp/conda-tmp

USER $UNAME
# Copy environment.yml (if found) to a temp location so we update the environment. Also
# copy "noop.txt" so the COPY instruction does not fail if no environment.yml exists.
COPY conda.yaml* .devcontainer/noop.txt /tmp/conda-tmp/
RUN if [ -f "/tmp/conda-tmp/environment.yml" ]; then umask 0002 && /opt/conda/bin/conda env update -n base -f /tmp/conda-tmp/conda.yaml; fi \
    && rm -rf /tmp/conda-tmp


FROM base AS prod 

# Install cloudflared
USER root
RUN wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && dpkg -i cloudflared-linux-amd64.deb
RUN chmod -R 777 /opt/conda

# Copy project files
COPY . /workspaces/interpreter-butlerhat
WORKDIR /workspaces/interpreter-butlerhat

# This is needed to avoid permissions errors when clonning with actions
RUN chown -R $UNAME:$UNAME /workspaces/interpreter-butlerhat

ENV DBUS_SESSION_BUS_ADDRESS="autolaunch:" \
    VNC_RESOLUTION="1280x720x16" \
    VNC_DPI="96" \
    VNC_PORT="5901" \
    NOVNC_PORT="6080" \
    DISPLAY=":1" \
    LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8"

USER $UNAME

COPY .devcontainer/prod/conda-prod.yaml /tmp/pip-tmp/conda-prod.yml
COPY .devcontainer/resolve_conda_secret.py /tmp/pip-tmp/resolve_conda_secret.py

WORKDIR /tmp/pip-tmp
RUN python resolve_conda_secret.py --token $GITHUB_TOKEN
RUN conda env update -n base -f conda_pass.yaml

CMD ["bash", "./.devcontainer/postCreateCommand.sh"]
