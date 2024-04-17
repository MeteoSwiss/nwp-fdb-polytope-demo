ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2404.305a50a169f4c9b420af1c2611aac4af5cdbe082

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
