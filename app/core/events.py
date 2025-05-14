from contextlib import asynccontextmanager
from fastapi import FastAPI
import subprocess
import app.core.config as config
from app.db.session import mongodb
from app.core.logger_setup import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    command = [
        "gcloud",
        "auth",
        "activate-service-account",
        f"--key-file={config.GOOGLE_APPLICATION_CREDENTIALS}",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger = setup_logger("lifespan_logger")
    logger.info(f"Starting application in {config.ENV} environment")

    if process.returncode != 0:
        logger.error(f"Google Cloud Authentication Error: {stderr.decode()}")
        raise RuntimeError("Failed to authenticate with Google Cloud")
    else:
        logger.info("Successfully authenticated with Google Cloud")

    await mongodb.connect()

    yield

    logger.info("Application is shutting down")
