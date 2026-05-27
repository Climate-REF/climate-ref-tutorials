# Pre-built JupyterLab image for the Climate REF training notebooks.
#
# Mirrors the Binder/repo2docker setup in .binder/ so users can pull a ready
# environment instead of waiting for Binder to build from scratch.
#
# Build:
#   docker build -t ghcr.io/climate-ref/climate-ref-tutorials:dev .
# Run:
#   docker run --rm -p 8888:8888 ghcr.io/climate-ref/climate-ref-tutorials:dev

FROM quay.io/jupyter/minimal-notebook:python-3.12

LABEL org.opencontainers.image.source="https://github.com/Climate-REF/climate-ref-tutorials"
LABEL org.opencontainers.image.description="JupyterLab environment for the Climate REF training notebooks"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Cartopy needs GEOS + PROJ system libraries (matches .binder/apt.txt).
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgeos-dev \
        libproj-dev \
        proj-bin \
        proj-data \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}
WORKDIR /home/${NB_USER}/work

# Install pinned Python deps first so this layer caches across source edits.
COPY --chown=${NB_UID}:${NB_GID} .binder/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir uv \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the rest of the repo and install the helper package + generated client.
COPY --chown=${NB_UID}:${NB_GID} . .
RUN pip install --no-cache-dir --no-deps . \
    && bash scripts/generate_client.sh \
    && python -c "from ref_tutorials import fetch_sample_data; fetch_sample_data()" \
    && python -c "import matplotlib.pyplot as plt; plt.figure(); plt.text(0, 0, 'warm fonts'); plt.close('all')"

# Use the non-interactive Agg backend by default (matches .binder/start).
ENV MPLBACKEND=Agg
