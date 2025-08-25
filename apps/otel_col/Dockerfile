# apps/otel_col/Dockerfile
FROM otel/opentelemetry-collector-contrib:0.94.0

COPY otel_config.yaml /etc/otelcol-config.yml

ENTRYPOINT ["/otelcol-contrib"]
CMD ["--config", "/etc/otelcol-config.yml"]
