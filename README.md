## Simple Implementation of RAG system using QDRANT, COLPALI Engine and Phi3Mini

### Steps to use

1. ``` mkdir data```
2. ```cd``` into the ```src``` directory
3. Install all dependencies using ```pip3 install -r requirements.txt```
4. Install Colpali engine using uv command by 
``` uv pip install --system colpali_engine>=0.3.1 datasets huggingface_hub[hf_transfer] qdrant-client transformers>=4.45.0 stamina rich ```
5. After installing all dependencies run the directory watcher which automates the embedding collection 
``` python -m helper_funcs.watcher```


### Parts Under Dev

- [x] Directory watcher for auto embedding
- [x] QDRANT collection creation
- [x] Embedding generation using Colpali
- [ ] GUI Development using streamlit
- [ ] RAG system integration  
- [ ] Composing everything into docker-compose