FROM nousresearch/hermes-agent@sha256:9774f4f39a9bb8c2f68ce728ed5e99ddbad282163be56764afacf88ed952b784
USER root
ARG ENGINE_REVISION
LABEL org.opencontainers.image.source="https://github.com/Zivoe/zivoe-underwriter" \
      org.opencontainers.image.revision=$ENGINE_REVISION
ENV UNDERWRITER_REVISION=$ENGINE_REVISION \
    CODEX_HOME=/logins/codex \
    ZIVOE_AI_BACKEND=codex \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
# Reuse the already pinned base layers; do not run Hermes bootstrap in this worker.
RUN python3 -m venv /opt/engine-venv
COPY source /opt/engine-source
RUN /opt/engine-venv/bin/pip install --no-cache-dir /opt/engine-source \
    && /opt/engine-venv/bin/pip freeze > /opt/engine-dependencies.txt
RUN npm install -g --prefix /usr/local @openai/codex@0.162.0 \
    && npm cache clean --force
RUN cp -a /opt/engine-source/config /opt/engine-config \
    && mkdir -p /logins/codex /home/engine \
    && chown -R 10000:10000 /logins /home/engine
ENV HOME=/home/engine
USER 10000:10000
WORKDIR /jobs
ENTRYPOINT ["/opt/engine-venv/bin/python"]
CMD ["/deployment/jobs/worker.py"]
