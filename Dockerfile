FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Copy optional files if they exist
COPY data.d[b] ./
COPY sensor_lstm.kera[s] ./
COPY mocked_data.cs[v] ./

ENV PYTHONPATH=/app/src

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]