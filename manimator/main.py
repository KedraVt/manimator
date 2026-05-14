from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import re
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from manimator.utils.schema import ManimProcessor
from manimator.utils.helpers import download_arxiv_pdf
from functools import lru_cache

from manimator.api.animation_generation import generate_animation_response
from manimator.api.scene_description import process_prompt_scene, process_pdf_prompt

load_dotenv()


class PromptRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        description="The text prompt to generate animation or scene description",
    )


class SceneDescriptionResponse(BaseModel):
    scene_description: str


class HealthCheckResponse(BaseModel):
    status: str


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend/index.html", "r") as f:
        return f.read()


@app.get("/health-check", response_model=HealthCheckResponse)
@limiter.limit("5/minute")
async def health_check(request: Request):
    return {"status": "ok"}


@app.post("/generate-pdf-scene", response_model=SceneDescriptionResponse)
@limiter.limit("5/minute")
async def generate_pdf_scene(request: Request, file: UploadFile = File(...)):
    try:
        content = await file.read()
        scene_description = process_pdf_prompt(content)
        return {"scene_description": scene_description}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail="An error occurred processing the PDF"
        )


@lru_cache(maxsize=128)
def cached_process_prompt_scene(prompt: str) -> str:
    return process_prompt_scene(prompt)


@app.post("/generate-prompt-scene", response_model=SceneDescriptionResponse)
@limiter.limit("10/minute")
async def generate_prompt_scene(request: Request, body: PromptRequest):
    try:
        return SceneDescriptionResponse(
            scene_description=cached_process_prompt_scene(body.prompt)
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail="Error generating scene descriptions"
        )


@lru_cache(maxsize=128)
def cached_process_arxiv(arxiv_id: str) -> str:
    arxiv_url = f"https://arxiv.org/pdf/{arxiv_id}"
    pdf_content = download_arxiv_pdf(arxiv_url)
    return process_pdf_prompt(pdf_content)


@app.get("/pdf/{arxiv_id}", response_model=SceneDescriptionResponse)
@limiter.limit("5/minute")
async def process_arxiv_by_id(request: Request, arxiv_id: str):
    """Process arxiv paper by ID"""
    try:
        scene_description = cached_process_arxiv(arxiv_id)
        return {"scene_description": scene_description}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail="An error occurred processing the arXiv ID"
        )


@app.post("/generate-animation")
@limiter.limit("2/minute")
async def generate_animation(request: Request, body: PromptRequest):
    processor = ManimProcessor()

    try:
        with processor.create_temp_dir() as temp_dir:
            response = generate_animation_response(body.prompt)
            code = processor.extract_code(response)
            if not code:
                raise HTTPException(
                    status_code=400, detail="No valid Manim code generated"
                )
            class_match = re.search(r"class (\w+)\(Scene\)", code)
            if not class_match:
                raise HTTPException(
                    status_code=400, detail="No Scene class found in code"
                )
            scene_name = class_match.group(1)
            scene_file = processor.save_code(code, temp_dir)
            video_path = processor.render_scene(scene_file, scene_name, temp_dir)
            if not video_path:
                raise HTTPException(
                    status_code=500, detail="Failed to render animation"
                )
            return FileResponse(video_path, media_type="video/mp4")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail="An error occurred generating the animation"
        )


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
