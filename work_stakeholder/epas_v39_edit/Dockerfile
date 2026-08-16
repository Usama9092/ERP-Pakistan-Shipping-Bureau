FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends clamav clamav-freshclam \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
ENV PYTHONUNBUFFERED=1
ENV EPAS_REQUIRE_ANTIVIRUS=1
COPY deployment/entrypoint_v36.sh /entrypoint_v36.sh
RUN chmod +x /entrypoint_v36.sh
ENTRYPOINT ["/entrypoint_v36.sh"]
