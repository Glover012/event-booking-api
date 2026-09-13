FROM python:3.14-slim

WORKDIR /event-booking-api

COPY requirements/requirements.lock requirements/

RUN pip install --no-cache-dir -r requirements/requirements.lock

COPY . .

RUN chmod +x docker/docker-entrypoint.sh

ENTRYPOINT ["./docker/docker-entrypoint.sh"]

CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0"]
