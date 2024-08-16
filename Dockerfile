# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the ports for FastAPI and Streamlit
EXPOSE 8000 8501

RUN pip install streamlit

# Start both the FastAPI server and Streamlit app using a shell script
CMD ["bash", "-c", "cd fastapi && uvicorn main:app --host 0.0.0.0 --port 8000 --reload & cd /app/streamlit && streamlit run main.py --server.port 8501 --server.address 0.0.0.0"]
# CMD ["bash", "-c", "cd fastapi && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
