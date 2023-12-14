ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2312.88ab9185fe3861a9c318a236eaebfb3cb341dd4e

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .
