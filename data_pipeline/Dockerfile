# ═══════════════════════════════════════════════════════════════
# AutoMind Data Pipeline — Docker Image
# Includes scrapers, Kafka producers, Spark jobs, Airflow DAGs
# ═══════════════════════════════════════════════════════════════

FROM python:3.11-slim

# System dependencies for building packages and running scrapers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY data_pipeline/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire data_pipeline module
COPY data_pipeline/ ./data_pipeline/

# Copy database migrations (for reference)
COPY database/ ./database/

# Copy topics config (shared)
COPY data_pipeline/kafka/topics_config.py ./data_pipeline/kafka/topics_config.py

# Ensure Python can find modules
ENV PYTHONPATH=/app

# Default command runs the scraper producer in dry-run mode
# Override with --live for actual scraping
CMD ["python", "-m", "data_pipeline.kafka.producers.scrapers.run_producer", "--dry-run"]