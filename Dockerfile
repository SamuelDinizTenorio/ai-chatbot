# ====================================================================================
# 1. Use an official, lightweight Python slim base image
# ====================================================================================
FROM python:3.11-slim

# ====================================================================================
# 2. Prevent interactive prompts and dialogues during apt package installation
# ====================================================================================
ENV DEBIAN_FRONTEND=noninteractive

# ====================================================================================
# 3. Configure environment variables optimized for containerized Python runtimes
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# PYTHONUNBUFFERED: Ensures application logs are streamed instantly to stdout/stderr
# ====================================================================================
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true

# ====================================================================================
# 4. Set the system working directory inside the container
# ====================================================================================
WORKDIR /app

# ====================================================================================
# 5. Install necessary OS-level dependencies, 
#    cleaning up caches to reduce image footprint
# ====================================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ====================================================================================
# 6. Copy dependency manifestation first to leverage Docker layer caching
# ====================================================================================
COPY requirements.txt .

# ====================================================================================
# 7. Install Python dependencies using pip without caching build artifacts
# ====================================================================================
RUN pip install --no-cache-dir -r requirements.txt

# ====================================================================================
# 8. Copy the remaining application source code into the working directory
# ====================================================================================
COPY . .

# ====================================================================================
# 9. Expose the default networking port Streamlit listens on
# ====================================================================================
EXPOSE 8501

# ===================================================================================
# 10. Define the default entrypoint instruction to execute the Streamlit application
# ===================================================================================
CMD ["streamlit", "run", "app.py"]
