ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2407.18e5e8c8747bf4564a03ed73bcc2ae67edb7a05d

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER use-case/src .

RUN mkdir /app/out
