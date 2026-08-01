FROM python:3.14-slim

WORKDIR /event-booking-api

COPY requirements.lock .

RUN pip install --no-cache-dir -r requirements.lock

COPY . .

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]

CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0"]
