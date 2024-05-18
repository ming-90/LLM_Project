PYTHON=3.10
BASENAME=$(shell basename $(CURDIR))

env:
	conda create -n $(BASENAME)  python=$(PYTHON) -y

setup:
	pip install -r requirements.txt

qdrant:
	docker run -p 6333:6333 -p 6334:6334 -v /opt/qdrant/single:/qdrant/storage:z qdrant/qdrant

run:
	streamlit run app.py --server.maxUploadSize 2500

run_node:
	nodemon --exec "streamlit run --server.maxUploadSize 2500" app.py -e py

run_server:
	cd server && uvicorn main:app --reload