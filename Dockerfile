ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
FROM ${container_registry}/mch/python/builder as mch-base

FROM ${container_registry}/numericalweatherpredictions/polytope-dependencies:2407.20f38c334c988422d60699558023b08dfc470a5d as dependencies

FROM quay.io/jupyter/base-notebook:python-3.11.8

USER root
COPY --from=mch-base /usr/local/share/ca-certificates/mchroot.crt /usr/local/share/ca-certificates/mchroot.crt
RUN update-ca-certificates

ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    PIP_INDEX='https://hub.meteoswiss.ch/nexus/repository/python-all/pypi' \
    PIP_INDEX_URL='https://hub.meteoswiss.ch/nexus/repository/python-all/simple' \
    PIP_NO_CACHE_DIR=0 \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

COPY --from=dependencies --chown=$NB_UID:$NB_GID /work/spack-root /work/spack-root
COPY --from=dependencies --chown=$NB_UID:$NB_GID /opt/fdb /opt/fdb
COPY --from=dependencies --chown=$NB_UID:$NB_GID /work/eccodes-cosmo-resources/definitions /opt/conda/share/eccodes-cosmo-resources/definitions

ENV PATH=/opt/fdb/bin:$PATH \
    GRIB_DEFINITION_PATH=/opt/conda/share/eccodes-cosmo-resources/definitions:/opt/conda/share/eccodes/definitions \
    FDB5_HOME=/opt/fdb \
    FDB_REMOTE_RETRIEVE_QUEUE_LENGTH=10

COPY --chown=$NB_UID:$NB_GID env.yaml /tmp/env.yaml

RUN mamba env update --file /tmp/env.yaml && \
    mamba clean --all --yes && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

USER $NB_USER
