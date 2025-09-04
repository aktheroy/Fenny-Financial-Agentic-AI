from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path
import json
import dotenv

# Add the project root to Python path to fix import issues
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Load environment variables
dotenv.load_dotenv()

# Set up logger first
logger = logging.getLogger("fenny")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Global variables for tools and LLM (will be initialized in lifespan)
tool_registry = None
execution_graph = None
finance_llm = None


# Use lifespan instead of on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    # Startup code
    logger.info("Starting Fenny Financial Assistant initialization...")

    global tool_registry, execution_graph, finance_llm

    try:
        # Import tools after ensuring path is correct
        from Backend.config import settings
        from Backend.core.session import session_manager

        # Initialize session manager
        session_manager = session_manager

        # Log configuration
        logger.info(
            f"Max files per conversation: {settings.MAX_FILES_PER_CONVERSATION}"
        )
        logger.info(f"Max file size: {settings.MAX_FILE_SIZE/1024/1024}MB")

        # Initialize tool registry
        try:
            from Backend.tools.tool_registry import ToolRegistry

            tool_registry = ToolRegistry()
            logger.info(
                f"Tool registry initialized with {len(tool_registry.tools)} tools"
            )

            # Initialize graph
            from Backend.graph.graph_builder import GraphBuilder

            graph_builder = GraphBuilder(tool_registry)
            graph_builder.add_tool_node()
            execution_graph = graph_builder.build()
            logger.info("Execution graph initialized")
        except Exception as e:
            logger.error(f"Failed to initialize tools and graph: {str(e)}")
            tool_registry = None
            execution_graph = None

        # Initialize LLM
        try:
            from Backend.llm.llm import FinanceLLM

            finance_llm = FinanceLLM()
            logger.info("Finance LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Finance LLM: {str(e)}")
            finance_llm = None

        # Verify frontend files exist
        frontend_dir = PROJECT_ROOT / "frontend"
        templates_dir = frontend_dir / "templates"
        static_dir = frontend_dir / "static"

        if not templates_dir.exists():
            logger.warning(f"Templates directory not found at {templates_dir}")
        if not static_dir.exists():
            logger.warning(f"Static directory not found at {static_dir}")

        yield  # Application runs here

    except Exception as e:
        logger.exception("Critical error during startup")
        yield
    finally:
        # Shutdown code
        logger.info("Shutting down Fenny Financial Assistant")


# Initialize FastAPI with lifespan
app = FastAPI(title="Fenny Financial Assistant", debug=True, lifespan=lifespan)

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
        html_path = PROJECT_ROOT / "frontend" / "templates" / "Fenny.html"
        if not html_path.exists():
            logger.error(f"HTML file not found at {html_path}")
            return HTMLResponse(
                content="<h1>Error: Frontend file not found</h1>"
                "<p>Make sure your project structure matches the expected format</p>",
                status_code=500,
            )

        with open(html_path, "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error serving Fenny.html: {str(e)}")
        return HTMLResponse(
            content="<h1>Error: Frontend file not found</h1>"
            "<p>Make sure your project structure matches the expected format</p>"
            f"<p>Error: {str(e)}</p>",
            status_code=500,
        )


@app.post("/api/chat")
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
        from Backend.core.session import session_manager

        if not session_id:
            session = session_manager.create_session()
        else:
            session = session_manager.get_session(session_id)
            if not session:
                session = session_manager.create_session()

        # Check file limits
        if len(files) > 0:
            # Validate file count
            if session.get_file_count() + len(files) > 3:  # Hardcoded for safety
                raise HTTPException(
                    status_code=400,
                    detail="Cannot upload more than 3 files in a conversation",
                )

            # Validate file types and sizes
            for file in files:
                # Check file size
                if file.size > 5 * 1024 * 1024:  # 5MB hardcoded for safety
                    raise HTTPException(
                        status_code=400,
                        detail=f"File {file.filename} exceeds size limit of 5MB",
                    )

                # Check file type
                file_ext = file.filename.split(".")[-1].lower()
                allowed_exts = [".pdf", ".xls", ".xlsx", ".txt"]

                if file_ext not in allowed_exts:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File type .{file_ext} not allowed. Only PDF, Excel, and TXT files are permitted.",
                    )

            # Add files to session
            session.add_files(len(files))

        # Log the message
        logger.info(f"Session {session.session_id} - User: {message}")

        # Initialize chat history (simplified for this example)
        chat_history = [
            {
                "role": "system",
                "content": "You are a financial expert assistant named Fenny.",
            },
            {"role": "user", "content": message},
        ]

        # Check if we need to use a tool
        global tool_registry, execution_graph, finance_llm

        bot_response = None

        # Stock price check
        if "stock" in message.lower() or any(
            ticker in message.upper()
            for ticker in ["AAPL", "MSFT", "TSLA", "GOOG", "AMZN", "NVDA"]
        ):
            if (
                tool_registry
                and execution_graph
                and tool_registry.has_tool("stock_price")
            ):
                # Extract ticker symbol (simplified approach)
                possible_tickers = [
                    "AAPL",
                    "MSFT",
                    "TSLA",
                    "GOOG",
                    "AMZN",
                    "NVDA",
                    "META",
                    "IBM",
                    "INTC",
                    "AMD",
                ]
                ticker = next(
                    (t for t in possible_tickers if t in message.upper()), "AAPL"
                )

                tool_node = execution_graph["nodes"]["tool_node"]
                tool_result = tool_node.execute_tool("stock_price", {"ticker": ticker})

                # CORRECTED: Properly handle nested tool response
                if tool_result.get("status") == "success":
                    # Unwrap the tool's response (it's nested)
                    tool_output = tool_result.get("output", {})

                    if tool_output.get("status") == "success":
                        stock_data = tool_output.get("output", {})
                        if "error" in stock_data:
                            bot_response = f"⚠️ {stock_data['error']}"
                        else:
                            # Format the stock data for display
                            bot_response = (
                                f"**{stock_data.get('name', ticker)} ({stock_data.get('ticker', ticker)})**\n\n"
                                f"💰 Current Price: **${stock_data.get('current_price', 'N/A')} {stock_data.get('currency', 'USD')}**\n"
                                f"📊 Today's Range: {stock_data.get('day_range', 'N/A')}\n"
                                f"🏦 Market Cap: {stock_data.get('market_cap', 'N/A')}"
                            )
                            # Add PE ratio if available
                            if stock_data.get("pe_ratio", "N/A") != "N/A":
                                bot_response += f"\n📈 P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}"
                    else:
                        error_msg = tool_output.get("message", "Unknown error")
                        bot_response = f"⚠️ Error checking stock price: {error_msg}"
                else:
                    error_msg = tool_result.get("message", "Unknown error")
                    bot_response = f"⚠️ Error checking stock price: {error_msg}"
            else:
                bot_response = "I'm having trouble accessing my stock price tool right now. Please try again later."

        # Currency conversion
        elif (
            "currency" in message.lower()
            or "exchange" in message.lower()
            or any(
                c in message.upper()
                for c in ["USD", "EUR", "JPY", "GBP", "CAD", "AUD", "INR"]
            )
        ):
            if (
                tool_registry
                and execution_graph
                and tool_registry.has_tool("currency_exchange")
            ):
                # Extract currencies (simplified approach)
                currency_codes = [
                    "USD",
                    "EUR",
                    "JPY",
                    "GBP",
                    "CAD",
                    "AUD",
                    "CHF",
                    "CNY",
                    "INR",
                ]
                currencies = [c for c in currency_codes if c in message.upper()]

                base = currencies[0] if len(currencies) > 0 else "USD"
                target = currencies[1] if len(currencies) > 1 else "EUR"

                # Extract amount if mentioned
                amount = 1.0
                for word in message.split():
                    if word.replace(".", "", 1).isdigit():
                        amount = float(word)
                        break

                tool_node = execution_graph["nodes"]["tool_node"]
                tool_result = tool_node.execute_tool(
                    "currency_exchange",
                    {"base": base, "target": target, "amount": amount},
                )

                # CORRECTED: Properly handle nested tool response
                if tool_result.get("status") == "success":
                    # Unwrap the tool's response (it's nested)
                    tool_output = tool_result.get("output", {})

                    if tool_output.get("status") == "success":
                        currency_data = tool_output.get("output", {})

                        # Log for debugging
                        logger.debug(f"Currency API response: {currency_data}")

                        # Check if we have valid data structure
                        if not isinstance(currency_data, dict):
                            bot_response = (
                                "⚠️ Error: Invalid response format from currency service"
                            )
                        elif "error" in currency_data:
                            bot_response = f"⚠️ {currency_data['error']}"
                        elif (
                            "base" not in currency_data or "target" not in currency_data
                        ):
                            # This debug will help identify what keys are actually present
                            available_keys = (
                                ", ".join(currency_data.keys())
                                if isinstance(currency_data, dict)
                                else "None"
                            )
                            logger.error(
                                f"Currency data missing base/target. Available keys: {available_keys}"
                            )
                            bot_response = (
                                "⚠️ Error: Incomplete data from currency service"
                            )
                        else:
                            # Safely get values with defaults
                            converted_amount = currency_data.get(
                                "converted_amount", "N/A"
                            )
                            rate = currency_data.get("rate", "N/A")

                            # Format the currency data for display
                            bot_response = (
                                f"💱 **Currency Exchange**\n\n"
                                f"{amount:,.2f} **{currency_data['base']}** = "
                                f"**{converted_amount:,.4f} {currency_data['target']}**\n"
                                f"💱 Exchange Rate: 1 {currency_data['base']} = {rate:,.4f} {currency_data['target']}"
                            )
                    else:
                        error_msg = tool_output.get("message", "Unknown error")
                        bot_response = f"⚠️ Error checking currency rates: {error_msg}"
                else:
                    error_msg = tool_result.get("message", "Unknown error")
                    bot_response = f"⚠️ Error checking currency rates: {error_msg}"
            else:
                bot_response = "I'm having trouble accessing my currency exchange tool right now. Please try again later."

        # Use LLM for non-tool queries
        if bot_response is None:
            if finance_llm:
                try:
                    # Format the prompt for the finance LLM
                    from Backend.llm.prompt_templates import get_finance_prompt

                    prompt = get_finance_prompt(chat_history)

                    # Generate response from LLM
                    bot_response = finance_llm.generate_response(
                        prompt, max_tokens=512, temperature=0.7
                    )

                    # Clean up response (remove any potential tool call formatting)
                    bot_response = (
                        bot_response.replace("Action:", "")
                        .replace("Action Input:", "")
                        .strip()
                    )
                except Exception as e:
                    logger.exception(f"Error generating LLM response: {str(e)}")
                    bot_response = (
                        "I encountered an issue while processing your request. "
                        "Please try asking your question in a different way."
                    )
            else:
                bot_response = (
                    "I'm having trouble accessing my financial knowledge base. "
                    "Please try again later or ask a different question."
                )

        # Log the response
        logger.info(f"Session {session.session_id} - Bot: {bot_response}")

        # Return response with file count
        return JSONResponse(
            {"response": bot_response, "file_count": session.get_file_count()}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing chat request: {str(e)}")
        return JSONResponse(
            {
                "response": f"⚠️ I encountered an error processing your request: {str(e)}",
                "file_count": session.get_file_count() if "session" in locals() else 0,
            },
            status_code=500,
        )


@app.post("/api/clear")
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
            raise HTTPException(status_code=400, detail="Session ID is required")

        # Remove session if it exists
        from Backend.core.session import session_manager

        session_manager.delete_session(session_id)

        return JSONResponse({"status": "success", "message": "Conversation cleared"})

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error clearing conversation")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    tool_count = 0
    llm_status = "not initialized"

    if "tool_registry" in globals() and tool_registry:
        tool_count = len(tool_registry.tools)

    if "finance_llm" in globals() and finance_llm:
        llm_status = "initialized"

    return {
        "status": "healthy",
        "message": "Fenny Financial Assistant is running",
        "tool_count": tool_count,
        "llm_status": llm_status,
        "tools": (
            list(tool_registry.tools.keys())
            if "tool_registry" in globals() and tool_registry
            else []
        ),
    }
