import os
import tempfile
from io import BytesIO
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import PyPDF2
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="PDF Genie", description="Transform boring PDFs into entertaining meme-style explanations")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
client = genai.Client(api_key=GEMINI_API_KEY)

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extract text from PDF bytes using PyPDF2.
    Returns the concatenated text from all pages.
    """
    try:
        # Create a BytesIO object from the uploaded file bytes
        pdf_stream = BytesIO(pdf_file)
        
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        
        # Extract text from all pages
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text() + "\n"
        
        return text_content.strip()
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text from PDF: {str(e)}")

def generate_meme_explanation(pdf_text: str) -> str:
    """
    Send the extracted PDF text to Gemini AI with meme-style system instructions.
    
    MODIFY THIS FUNCTION TO CHANGE THE AI PROMPT:
    - Update the system_instruction to change the AI's personality
    - Modify the user prompt format to change how the text is presented
    - Adjust the model parameters for different response styles
    """
    try:
        # System instruction that defines PDF Genie's personality and style
        # CUSTOMIZATION POINT: Modify this to change the AI's response style
        system_instruction = (
            "You are PDF Genie 🧞‍♂️ Your job is to turn boring PDFs (manuals, legal docs, "
            "textbooks, policies, reports) into LENGTHY, hilarious, meme-style explainers that "
            "anyone can understand. Make your responses LONG and DETAILED - users want to read "
            "extensive, entertaining content! Break down concepts with lots of examples, analogies, "
            "and stories. Use tons of emojis, bullet points, numbered lists, and humor. "
            "Add pop culture references, internet slang, and memes throughout. Write like you're "
            "telling a funny story to your best friend, not a formal report. Include multiple "
            "sections, elaborate on details, and make it as entertaining as possible. "
            "The longer and funnier, the better! Think of it like creating viral TikTok content "
            "but in text form. Use headings, subheadings, and lots of formatting to make it engaging."
        )
        
        # Format the user prompt
        # CUSTOMIZATION POINT: Change this to modify how the PDF content is presented to the AI
        user_prompt = (
            f"Here's the content from a PDF that needs your magic touch! "
            f"Transform this into a LONG, entertaining explanation. "
            f"Make it extensive tons of examples, stories, and humor. "
            f"Users love reading long, funny content - so go wild with the details!\n\n"
            f"PDF CONTENT:\n{pdf_text[:12000]}"  # Increased limit for more content
        )
        
        # Generate content using Gemini
        # CUSTOMIZATION POINT: You can change the model here (gemini-2.5-flash is faster, gemini-2.5-pro is more capable)
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Use flash model for faster responses
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.9,  # Higher temperature for more creative/funny responses
                max_output_tokens=2500,  # Increased limit for longer, detailed responses
            ),
        )
        
        if response.text:
            return response.text
        else:
            raise Exception("Empty response from Gemini AI")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main HTML page"""
    try:
        # Update to use UTF-8 encoding explicitly
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend not found")

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Main endpoint for PDF upload and processing.
    
    Process:
    1. Validate the uploaded file is a PDF
    2. Extract text using PyPDF2
    3. Send to Gemini AI for meme-style explanation
    4. Return the entertaining explanation
    """
    
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a PDF file. 📄"
        )
    
    # Validate file size (limit to 10MB)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=400,
            detail="File too large. Please upload a PDF smaller than 10MB. 🚫"
        )
    
    try:
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(file_content)
        
        # Check if we extracted any meaningful text
        if not pdf_text or len(pdf_text.strip()) < 50:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "Hmm, this PDF seems to be mostly images or has very little text. 🤔 PDF Genie works best with text-heavy documents!"
                }
            )
        
        # Generate meme-style explanation using Gemini AI
        explanation = generate_meme_explanation(pdf_text)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "explanation": explanation,
                "original_length": len(pdf_text),
                "filename": file.filename
            }
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (these already have proper error messages)
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Oops! Something went wrong while processing your PDF. 😅 Error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "PDF Genie", "version": "1.0"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    # Bind to 0.0.0.0:5000 as specified in the requirements
    uvicorn.run(app, host="0.0.0.0", port=5000)
