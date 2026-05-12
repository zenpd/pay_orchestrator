FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_MODE=multiregion

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements_web.txt ./
RUN pip install --no-cache-dir -r requirements_web.txt

COPY . .

# Create supervisor config for running both API and Streamlit
RUN mkdir -p /etc/supervisor/conf.d && \
    echo "[supervisord]" > /etc/supervisor/conf.d/services.conf && \
    echo "nodaemon=true" >> /etc/supervisor/conf.d/services.conf && \
    echo "logfile=/var/log/supervisord.log" >> /etc/supervisor/conf.d/services.conf && \
    echo "pidfile=/var/run/supervisord.pid" >> /etc/supervisor/conf.d/services.conf && \
    echo "" >> /etc/supervisor/conf.d/services.conf && \
    echo "[program:api]" >> /etc/supervisor/conf.d/services.conf && \
    echo "command=python api_server.py" >> /etc/supervisor/conf.d/services.conf && \
    echo "directory=/app" >> /etc/supervisor/conf.d/services.conf && \
    echo "autostart=true" >> /etc/supervisor/conf.d/services.conf && \
    echo "autorestart=true" >> /etc/supervisor/conf.d/services.conf && \
    echo "stderr_logfile=/var/log/api.err.log" >> /etc/supervisor/conf.d/services.conf && \
    echo "stdout_logfile=/var/log/api.out.log" >> /etc/supervisor/conf.d/services.conf && \
    echo "priority=999" >> /etc/supervisor/conf.d/services.conf && \
    echo "" >> /etc/supervisor/conf.d/services.conf && \
    echo "[program:streamlit]" >> /etc/supervisor/conf.d/services.conf && \
    echo "command=streamlit run streamlit_ui.py --server.port=8501 --server.headless=true" >> /etc/supervisor/conf.d/services.conf && \
    echo "directory=/app" >> /etc/supervisor/conf.d/services.conf && \
    echo "autostart=true" >> /etc/supervisor/conf.d/services.conf && \
    echo "autorestart=true" >> /etc/supervisor/conf.d/services.conf && \
    echo "stderr_logfile=/var/log/streamlit.err.log" >> /etc/supervisor/conf.d/services.conf && \
    echo "stdout_logfile=/var/log/streamlit.out.log" >> /etc/supervisor/conf.d/services.conf && \
    echo "priority=1000" >> /etc/supervisor/conf.d/services.conf && \
    echo "" >> /etc/supervisor/conf.d/services.conf && \
    echo "[inet_http_server]" >> /etc/supervisor/conf.d/services.conf && \
    echo "port=127.0.0.1:9001" >> /etc/supervisor/conf.d/services.conf && \
    echo "" >> /etc/supervisor/conf.d/services.conf && \
    echo "[supervisorctl]" >> /etc/supervisor/conf.d/services.conf && \
    echo "serverurl=http://127.0.0.1:9001" >> /etc/supervisor/conf.d/services.conf && \
    echo "" >> /etc/supervisor/conf.d/services.conf && \
    echo "[rpcinterface:supervisor]" >> /etc/supervisor/conf.d/services.conf && \
    echo "supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface" >> /etc/supervisor/conf.d/services.conf

EXPOSE 8000 8501 9001

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/../supervisord.conf"]
