ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2404.c6ffdf120e50ce2433b194ee9bef0b66881a9b4e

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
