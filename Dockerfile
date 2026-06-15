FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY src ./src
COPY data/processed ./data/processed

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "src/app/ui/streamlit_app.py", \
     "--server.headless=true", "--server.address=0.0.0.0", "--server.port=8501"]
