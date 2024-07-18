FROM python:3.10-slim-bullseye
EXPOSE 3000
# Set the working directory
WORKDIR /app

ENV VIRTUAL_ENV=/usr/local

# Install dependencies
COPY requirements.txt ./
RUN apt-get update
RUN apt-get install -y gcc 
RUN pip install --upgrade pip=="24.0" && pip install uv=="0.1.29" && uv pip install --no-cache -r requirements.txt

# Copy the project files
COPY main.py ./
COPY api/ ./api/
COPY models/ ./models/
COPY utils ./utils/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]
