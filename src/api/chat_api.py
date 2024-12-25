from fastapi import FastAPI, HTTPException
from helper_funcs.colpali_helper import colpali_processor, colpali_model
from helper_funcs.qdrant_helper import qdrant_client, collection_name
from qdrant_client.http import models
from pydantic import BaseModel
import requests
import torch


app = FastAPI()

# Define the request and response model for the API
class MessageRequest(BaseModel):
    message: str

class ModelResponse(BaseModel):
    response: str

# URL for the Ollama model (adjust if needed)
OLLAMA_URL = "http://localhost:11434/api/generate"  # Update this URL as per your setup







@app.post("/send-message", response_model=ModelResponse)
def send_message_to_model(request: MessageRequest):
    """
    Sends a user message to the Ollama model and returns the model's response.
    """
    try:
        # Payload to send to the model
        query = request.message
        
        with torch.no_grad():
            batch_query = colpali_processor.process_queries([query]).to(colpali_model.device)
            query_embedding = colpali_model(**batch_query)
            multivector_query = query_embedding[0].cpu().float().numpy().tolist()
        
        search_result = qdrant_client.query_points(
            collection_name=collection_name,
            query=multivector_query,
            limit=10,
            timeout=100,
            search_params=models.SearchParams(
                quantization=models.QuantizationSearchParams(
                    ignore=False,
                    rescore=True,
                    oversampling=2.0,
                )
            )
        )

        most_related_doc = search_result.points[0]

        prompt = f"""
        Answer the question: {query}
        using the context: {most_related_doc}
"""


        payload = {"model": "phi3:mini","prompt": request.message, "stream": False}

        # Send the message to the Ollama model
        response = requests.post(OLLAMA_URL, json=payload)

        # Check if the request to the model was successful
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error communicating with the Ollama model.")

        # Parse the model's response
        model_output = response.json()
        return ModelResponse(response=model_output.get("response", "No response from the model"))

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
