ARG container_registry=dockerhub.apps.cp.meteoswiss.ch
ARG base_image_tag=2402.12058b28b8e791281053dbe733d76867f7f03eca

FROM ${container_registry}/numericalweatherpredictions/polytope/demo/base:${base_image_tag}

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=$MAMBA_USER:$MAMBA_USER demo/use-case/src .

RUN mkdir /app/out
