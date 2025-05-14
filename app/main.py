from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import general_routes, ai_routes, db_routes, health_check
from app.core.events import lifespan
from app.core.logger_setup import setup_logger, request_id_ctx
import uuid

logger = setup_logger("main_logger")
app = FastAPI(lifespan=lifespan, docs_url="/docs", root_path="/api")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_ctx.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(health_check.router)
app.include_router(general_routes.router)
app.include_router(ai_routes.router)
app.include_router(db_routes.router)
