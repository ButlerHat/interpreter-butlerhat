FROM mcr.microsoft.com/devcontainers/miniconda:0-3 AS base

ARG UNAME=vscode
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG PYPI_USER
ARG PYPI_PASS
ARG GITHUB_TOKEN

USER root

# Change timezone
ENV TZ='/usr/share/zoneinfo/Europe/Madrid'
RUN sudo ln -snf $TZ /etc/localtime && echo "Europe/Madrid" > /etc/timezone

# Install robotframework env
ENV PIP_EXTRA_INDEX_URL=https://$PYPI_USER:$PYPI_PASS@pypiserver.paipaya.com/

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends poppler-utils ffmpeg libsm6 libxext6 scrot

# Install chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get -y install ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

ENV PATH=/home/$UNAME/.local/bin:$PATH

ENV DBUS_SESSION_BUS_ADDRESS="autolaunch:" \
    VNC_RESOLUTION="1440x768x16" \
    VNC_DPI="96" \
    VNC_PORT="5901" \
    NOVNC_PORT="6080" \
    DISPLAY=":1" \
    LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8"

RUN mkdir -p /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/interpreter-butlerhat/.devcontainer && chown -R $UNAME:$UNAME /workspaces
WORKDIR /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/interpreter-butlerhat
USER $UNAME

COPY conda.yaml ./conda.yaml
COPY .devcontainer/robocorp-python-ls-core-0.0.0.tar.gz .devcontainer/robocorp-python-ls-core-0.0.0.tar.gz
COPY .devcontainer/robotframework-interactive-0.0.1.tar.gz .devcontainer/robotframework-interactive-0.0.1.tar.gz
RUN umask 0002 && conda env create -n robotframework -f ./conda.yaml
RUN conda init bash
RUN echo "conda activate robotframework" >> ~/.bashrc



FROM base AS pre_prod 

# Variables
ENV PIP_EXTRA_INDEX_URL=https://$PYPI_USER:$PYPI_PASS@pypiserver.paipaya.com/
ENV DBUS_SESSION_BUS_ADDRESS="autolaunch:" \
    VNC_RESOLUTION="1280x720x16" \
    VNC_DPI="96" \
    VNC_PORT="5901" \
    NOVNC_PORT="6080" \
    DISPLAY=":1" \
    LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8"

# Install cloudflared
USER root

RUN mkdir -p /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/interpreter-butlerhat/.devcontainer/prod_gpt4 && chown -R $UNAME:$UNAME /workspaces
WORKDIR /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/interpreter-butlerhat

USER $UNAME


FROM pre_prod AS prod

# Install conda env
COPY .devcontainer/prod/conda.yaml .devcontainer/prod/conda.yaml
RUN conda env update -n robotframework -f .devcontainer/prod/conda.yaml --prune
RUN unset PIP_EXTRA_INDEX_URL

# For using npm installed in conda
ENV PATH=/opt/conda/envs/robotframework/bin:$PATH
RUN /opt/conda/envs/robotframework/bin/python -m Browser.entry init

# Copy project files
COPY . /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/interpreter-butlerhat
USER root
RUN chown -R $UNAME:$UNAME /workspaces
USER $UNAME

CMD ["bash", "./.devcontainer/prod/postCreateCommand.sh"]



FROM pre_prod AS prod_gpt4

# Install conda env
COPY .devcontainer/prod_gpt4/conda.yaml .devcontainer/prod_gpt4/conda.yaml
RUN conda env update -n robotframework -f .devcontainer/prod_gpt4/conda.yaml --prune
RUN unset PIP_EXTRA_INDEX_URL

# For using npm installed in conda
ENV PATH=/opt/conda/envs/robotframework/bin:$PATH
RUN /opt/conda/envs/robotframework/bin/python -m Browser.entry init

# Copy project files
COPY . /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/interpreter-butlerhat
USER root
RUN chown -R $UNAME:$UNAME /workspaces
USER $UNAME

CMD ["bash", "./.devcontainer/prod_gpt4/postCreateCommand.sh"]
