ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2402.d3df5ef1cf467b46d37ead547a1b4f677ed17a22

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .
