.PHONY: run

run:
	@echo "Starting FastAPI server..."
	@cd fastapi && uvicorn main:app --host 0.0.0.0 --port 8000 --reload & \
	echo "Starting Streamlit app..." && \
	streamlit run streamlit/main.py