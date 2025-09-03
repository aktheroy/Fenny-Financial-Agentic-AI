from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    Request,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import logging
from datetime import datetime
from contextlib import asynccontextmanager
import os
from pathlib import Path

# Local imports
from config import settings
from core.session import session_manager
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


# Use lifespan instead of on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    # Startup code
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Max files per conversation: {settings.MAX_FILES_PER_CONVERSATION}")
    logger.info(f"Max file size: {settings.MAX_FILE_SIZE/1024/1024}MB")

    # Verify frontend files exist
    frontend_dir = PROJECT_ROOT / "frontend"
    templates_dir = frontend_dir / "templates"
    static_dir = frontend_dir / "static"

    if not templates_dir.exists():
        logger.warning(f"Templates directory not found at {templates_dir}")
    if not static_dir.exists():
        logger.warning(f"Static directory not found at {static_dir}")

    yield  # Application runs here

    # Shutdown code (optional)
    logger.info(f"Shutting down {settings.APP_NAME}")


# Initialize FastAPI with lifespan
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=PROJECT_ROOT / "frontend" / "static"),
    name="static",
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML file"""
    try:
        with open(PROJECT_ROOT / "frontend" / "templates" / "Fenny.html", "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error serving Fenny.html: {str(e)}")
        return HTMLResponse(
            content="<h1>Error: Frontend file not found</h1>"
            "<p>Make sure your project structure matches the expected format</p>"
            f"<p>Error: {str(e)}</p>",
            status_code=500,
        )


@app.post(f"{settings.API_PREFIX}/chat")
async def chat(
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    files: List[UploadFile] = File([]),
):
    """
    Handle chat requests with optional file uploads

    Expected request:
    - message: str (form data)
    - session_id: str (form data, optional)
    - files: List[UploadFile] (files, optional)

    Returns:
    {
        "response": str,
        "file_count": int
    }
    """
    try:
        # Validate message
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Get or create session
        if not session_id:
            session = session_manager.create_session()
        else:
            session = session_manager.get_session(session_id)
            if not session:
                session = session_manager.create_session()

        # Check file limits
        if len(files) > 0:
            # Validate file count
            if (
                session.get_file_count() + len(files)
                > settings.MAX_FILES_PER_CONVERSATION
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot upload more than {
                        settings.MAX_FILES_PER_CONVERSATION
                        } files in a conversation",
                )

            # Validate file types and sizes
            for file in files:
                # Check file size
                if file.size > settings.MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File {file.filename} exceeds size limit of {
                            settings.MAX_FILE_SIZE/1024/1024
                            }MB",
                    )

                # Check file type
                file_ext = file.filename.split(".")[-1].lower()
                allowed_exts = [
                    ext[1:] for ext in settings.ALLOWED_FILE_EXTENSIONS
                    ]

                if (
                    file.content_type not in settings.ALLOWED_FILE_TYPES
                    and file_ext not in allowed_exts
                ):
                    raise HTTPException(
                        status_code=400,
                        detail=f"File type .{file_ext} not allowed. Only {', '.join(settings.ALLOWED_FILE_EXTENSIONS)} files are permitted.",
                    )

            # Add files to session
            session.add_files(len(files))

        # Log the message
        logger.info(f"Session {session.session_id} - User: {message}")

        # In a real implementation, this is where we'd call the LLM
        # For now, we'll just return appropriate responses based on the message
        if message.lower() in ["hi", "hello", "hey"]:
            bot_response = (
                "Hi, I'm Fenny! How can I help you today? Feel free to ask me any question on finance, "
                "investing, and also feel free to upload any financial documents for analysis."
            )
        elif "stock" in message.lower() or "price" in message.lower():
            bot_response = (
                "I can help you check stock prices. In a real implementation, I would connect "
                "to a financial API to get the latest stock data."
            )
        elif "analysis" in message.lower() or "report" in message.lower():
            if session.get_file_count() > 0:
                bot_response = (
                    "I've analyzed the financial documents you uploaded. In a real implementation, "
                    "I would provide specific insights based on the content of those documents."
                )
            else:
                bot_response = (
                    "I'd be happy to analyze financial documents. Please upload a PDF, Excel, "
                    "or text file containing financial data for me to review."
                )
        else:
            bot_response = (
                "Thanks for your message. In a real implementation, I would analyze your "
                "financial query and provide a helpful response based on my training "
                "and any documents you've shared."
            )

        # Log the response
        logger.info(f"Session {session.session_id} - Bot: {bot_response}")

        # Return response with file count (as integer, not string!)
        return JSONResponse(
            {
                "response": bot_response,
                "file_count": session.get_file_count(),  # This is now a proper integer
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again."
        )


@app.post(f"{settings.API_PREFIX}/clear")
async def clear_conversation(request: Request):
    """
    Clear a conversation session

    Expected request:
    - session_id: str (form data)

    Returns:
    {
        "status": "success",
        "message": "Conversation cleared"
    }
    """
    try:
        # Parse form data
        form = await request.form()
        session_id = form.get("session_id")

        if not session_id:
            raise HTTPException(
                status_code=400,
                detail="Session ID is required"
                )

        # Remove session if it exists
        session_manager.delete_session(session_id)

        return JSONResponse({
            "status": "success",
            "message": "Conversation cleared"
            })

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error clearing conversation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error clearing conversation")


@app.get(f"{settings.API_PREFIX}/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "sessions": len(session_manager.sessions),
        "max_files_per_conversation": settings.MAX_FILES_PER_CONVERSATION,
        "app_name": settings.APP_NAME,
    }
