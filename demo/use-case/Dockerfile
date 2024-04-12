ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2404.44da29df0fd99e84ad201427659e7e4f2b386394

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
