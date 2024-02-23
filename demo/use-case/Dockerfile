ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2402.4bad2b8aee083fb1a1867ce3d4e8480747c33d9e

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
