ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2312.2069a4031df1f81f87e9fb289e59b22bbab5a7b9

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

ENV PATH=/opt/conda/bin:$PATH

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .
