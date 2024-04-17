ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
FROM ${container_registry}/mch/python/builder as mch-base

RUN git clone --depth 1 --branch revise_mars_model https://github.com/cosunae/eccodes-cosmo-resources.git

FROM ${container_registry}/numericalweatherpredictions/polytope-dependencies:2404.8afab0fd961ea7c536bfb4ae88771b9c3d217235 as dependencies

FROM ${container_registry}/mambaorg/micromamba:1.5.8-jammy AS base

USER root
COPY --from=mch-base /usr/local/share/ca-certificates/mchroot.crt /usr/local/share/ca-certificates/mchroot.crt
RUN apt update && \
    apt install --no-install-recommends -y ca-certificates && \
    update-ca-certificates

ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    PIP_INDEX='https://hub.meteoswiss.ch/nexus/repository/python-all/pypi' \
    PIP_INDEX_URL='https://hub.meteoswiss.ch/nexus/repository/python-all/simple' \
    PIP_NO_CACHE_DIR=0

COPY --from=dependencies --chown=$MAMBA_USER:$MAMBA_USER /work/spack-root /work/spack-root
COPY --from=dependencies --chown=$MAMBA_USER:$MAMBA_USER /opt/fdb /opt/fdb
COPY --from=mch-base --chown=$MAMBA_USER:$MAMBA_USER /src/eccodes-cosmo-resources/definitions /opt/conda/share/eccodes-cosmo-resources/definitions

ENV PATH=/opt/conda/bin:/opt/fdb/bin:$PATH \
    GRIB_DEFINITION_PATH=/opt/conda/share/eccodes-cosmo-resources/definitions:/opt/conda/share/eccodes/definitions \
    FDB5_HOME=/opt/fdb

USER $MAMBA_USER

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/base-image/env.yaml /tmp/env.yaml

RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes

WORKDIR /app

USER root
RUN chown -R $MAMBA_USER:$MAMBA_USER /app
USER $MAMBA_USER
