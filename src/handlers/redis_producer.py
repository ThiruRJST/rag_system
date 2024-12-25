import asyncio
import aioredis
import pickle
import base64

redis_url = "redis://localhost:6379"


async def put_images_in_queue(queue_name, images):
    # Connect to Redis
    redis = await aioredis.from_url(redis_url)
    try:
        # Serialize the images
        serialized_images = [
            base64.b64encode(pickle.dumps(image)).decode("utf-8") for image in images
        ]

        # Put the serialized images in the queue
        await redis.rpush(queue_name, *serialized_images)
    finally:
        # Close the connection
        await redis.close()
        
