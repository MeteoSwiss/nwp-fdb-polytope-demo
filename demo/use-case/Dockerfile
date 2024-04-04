ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2404.453879ea84689bafb95d0bb00c7539983525ed6f

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
