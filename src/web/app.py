import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from tempfile import NamedTemporaryFile
import shutil

# Import our processors
from ..processor.image_processor import ImageProcessor
from ..processor.latex_processor import LatexProcessor
from ..processor.footnote_processor import FootnoteProcessor
from ..processor.heading_processor import HeadingProcessor
from ..converter import convert_pdf_to_markdown

app = FastAPI(title="PDF to Markdown Converter")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Get the directory containing this file
current_dir = Path(__file__).parent

# Setup templates and static files
templates = Jinja2Templates(directory=str(current_dir / "templates"))
app.mount("/static", StaticFiles(directory=str(current_dir / "static")), name="static")

class ConversionResponse(BaseModel):
    markdown: str
    images: Optional[list] = None
    toc: Optional[str] = None
    message: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/convert", response_model=ConversionResponse)
async def convert_pdf(file: UploadFile = File(...)):
    """Convert uploaded PDF to markdown."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    try:
        # Save uploaded file temporarily
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            shutil.copyfileobj(file.file, tmp_pdf)
            tmp_path = tmp_pdf.name
            
        try:
            # Convert PDF to markdown
            markdown, images, toc = convert_pdf_to_markdown(
                tmp_path,
                image_processor=ImageProcessor(),
                latex_processor=LatexProcessor(),
                footnote_processor=FootnoteProcessor(),
                heading_processor=HeadingProcessor()
            )
        except Exception as e:
            # Log the error but continue with conversion
            print(f"Warning: {str(e)}")
            # Try conversion without image processing
            markdown, images, toc = convert_pdf_to_markdown(
                tmp_path,
                image_processor=None,
                latex_processor=LatexProcessor(),
                footnote_processor=FootnoteProcessor(),
                heading_processor=HeadingProcessor()
            )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return ConversionResponse(
            markdown=markdown,
            images=images,
            toc=toc,
            message="Conversion successful"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/preview/{filename}")
async def preview_markdown(filename: str):
    """Preview converted markdown."""
    output_dir = Path("output")
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path)

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the web server."""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
