ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2402.76c08dd3ecfa077c71f769975f35fc59ded690e0

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
