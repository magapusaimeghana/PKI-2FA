 # Stage 1: builder
 FROM python:3.11-slim AS builder
 WORKDIR /build
 RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
 COPY app/requirements.txt .
 RUN python -m pip install --upgrade pip
 RUN pip wheel --wheel-dir=/wheels -r requirements.txt
 # Stage 2: runtime
 FROM python:3.11-slim
 ENV TZ=UTC
 WORKDIR /app
 RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/*
 COPY --from=builder /wheels /wheels
 RUN pip install --no-index --find-links=/wheels -r /build/requirements.txt
 COPY app /app
 COPY cron/2fa-cron /etc/cron.d/2fa-cron
 COPY student_private.pem /app/student_private.pem
 COPY student_public.pem /app/student_public.pem
 COPY instructor_public.pem /app/instructor_public.pem
 RUN chmod 0644 /etc/cron.d/2fa-cron \
 && crontab /etc/cron.d/2fa-cron
 RUN mkdir -p /data /cron
 VOLUME ["/data", "/cron"]
 EXPOSE 8080
 CMD service cron start && uvicorn main:app --host 0.0.0.0 --port 8080