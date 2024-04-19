ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2404.b1d201a79594e2b7472f582a1d1e2d5b9c3cee06

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
