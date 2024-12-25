import aioredis
import asyncio
import base64
import pickle
import torch

from colpali_engine.models import ColPali, ColPaliProcessor
from qdrant_client.http import models
from helper_funcs.qdrant_helper import upsert_to_qdrant
from tqdm import tqdm


# Initialize ColPali model and processor
model_name = (
    "davanstrien/finetune_colpali_v1_2-ufo-4bit"  # Use the latest version available
)
colpali_model = ColPali.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",  # Use "cuda:0" for GPU, "cpu" for CPU, or "mps" for Apple Silicon
)
colpali_processor = ColPaliProcessor.from_pretrained(
    "vidore/colpaligemma-3b-pt-448-base"
)

redis_url = "redis://localhost:6379"

def indexing_func(dataset, batch_size=2):
    # Use tqdm to create a progress bar
    points = []
    with tqdm(total=len(dataset), desc="Indexing Progress") as pbar:
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i : i + batch_size]

            # Process and encode images
            with torch.no_grad():
                batch_images = colpali_processor.process_images(batch).to(
                    colpali_model.device
                )
                image_embeddings = colpali_model(**batch_images)

            # # Prepare points for Qdrant
            # points = []
            for j, embedding in enumerate(image_embeddings):
                # Convert the embedding to a list of vectors
                multivector = embedding.cpu().float().numpy().tolist()
                points.append(
                    models.PointStruct(
                        id=i + j,  # we just use the index as the ID
                        vector=multivector,  # This is now a list of vectors
                        payload={
                            "source": "company pdf file"
                        },  # can also add other metadata/data
                    )
                )
            # Update the progress bar
            pbar.update(batch_size)

    # Upload points to Qdrant
    try:
        upsert_to_qdrant(points)
        print("Indexing complete")
    except Exception as e:
        print(f"Error during upsert: {e}")
                 
    


async def consume_images_from_queue(queue_name: str):
    # Connect to Redis
    redis = await aioredis.from_url(redis_url)
    try:
        while True:
            # Get the serialized images from the queue
            serialized_images = await redis.blpop(queue_name)
            if serialized_images is None:
                break

            # Deserialize the images
            images = [pickle.loads(base64.b64decode(image)) for image in serialized_images]

            # Index the images
            indexing_func(images)
    finally:
        # Close the connection
        await redis.close()