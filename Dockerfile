ARG container_registry=dockerhub.apps.cp.meteoswiss.ch

FROM ${container_registry}/mch/python/builder as mch-base 

RUN git clone --depth 1 --branch v2.35.0.1dm1 https://github.com/COSMO-ORG/eccodes-cosmo-resources.git /src/eccodes-cosmo-resources
RUN git clone --depth 1 --branch 2.35.0 https://github.com/ecmwf/eccodes.git /src/eccodes

FROM ${container_registry}/numericalweatherpredictions/polytope-dependencies:2504.8619f4553a9788479581841697255d675b0d9520 as dependencies

FROM dockerhub.apps.cp.meteoswiss.ch/mch/python-3.11:latest AS base

COPY --from=dependencies /work/spack-root /work/spack-root
COPY --from=dependencies /opt/fdb /opt/fdb
COPY --from=mch-base /src/eccodes/definitions /src/eccodes/definitions
COPY --from=mch-base /src/eccodes-cosmo-resources/definitions /src/eccodes-cosmo-resources/definitions
RUN mkdir -p spack-env/.spack-env && \
    ln -s /opt/fdb spack-env/.spack-env/view 


RUN pipx upgrade poetry

WORKDIR /src/app-root

COPY poetry.lock pyproject.toml /src/app-root/
RUN poetry install --only main

ENV PATH=/opt/fdb/bin:$PATH \
    GRIB_DEFINITION_PATH=/src/eccodes-cosmo-resources/definitions:/src/eccodes/definitions \
    FDB5_HOME=/opt/fdb \
    ECCODES_DIR=/opt/fdb


FROM base AS notebook

ENV FDB_REMOTE_RETRIEVE_QUEUE_LENGTH=10

COPY notebooks/ ./notebooks
RUN poetry install --with notebook

EXPOSE 8888
ENTRYPOINT ["poetry", "run", "jupyter-lab", "--allow-root", "--ip=0.0.0.0", "--port=8888", "--no-browser"]


FROM base AS use-case

COPY nwp_polytope_demo ./nwp_polytope_demo

RUN mkdir /src/app-root/out

