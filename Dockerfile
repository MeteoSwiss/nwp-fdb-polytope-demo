ARG container_registry=dockerhub.apps.cp.meteoswiss.ch

FROM quay.io/jupyter/base-notebook:python-3.11 as notebook

FROM notebook as tester

USER jovyan

COPY --chown=jovyan notebooks/ ./notebooks
COPY --chown=jovyan verify_clear.sh .
RUN chmod +x ./verify_clear.sh

ENTRYPOINT ["./verify_clear.sh"]

