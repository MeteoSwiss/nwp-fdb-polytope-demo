ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2403.98c943ee4dc6576690c383621f43fb653bdf4f93

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
