ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2404.f17b2395c09f764328d460e41247e99a4bca5e65

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
