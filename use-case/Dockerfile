ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2502.7f3dba1c17f7e023f06bb462e192482f32d34492

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER use-case/src .

RUN mkdir /app/out
