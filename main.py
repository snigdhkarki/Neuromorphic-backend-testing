from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware # 1. Import the middleware
import subprocess
import tempfile
import os

app = FastAPI()

# 2. Add the CORS middleware to your app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows requests from your React app
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (POST, GET, etc.)
    allow_headers=["*"], # Allows all headers
)

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    # 1. Read the uploaded file content
    input_content = await file.read()
    
    # 2. Create a temporary output file path
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".txt").name

    try:
        # 3. Execute your binary.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_input:
            tmp_input.write(input_content)
            input_path = tmp_input.name
        
        # ADDED: stderr=subprocess.PIPE and text=True to capture the binary's actual output text
        result = subprocess.run(
            f"./network_tool < {input_path} > {output_path}",
            shell=True,
            check=True,
            executable="/bin/bash",
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 4. Read the generated output file
        with open(output_path, "rb") as f:
            output_content = f.read()
            
        # 5. Return the file as a download
        return Response(
            content=output_content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=out.txt"}
        )
        
    except subprocess.CalledProcessError as e:
        # UPDATED: If the binary prints an error message, surface that instead of just "exit status 1"
        binary_error = e.stderr.strip() if e.stderr else str(e)
        return Response(content=f"Binary Error: {binary_error}", status_code=500)
    except Exception as e:
        return Response(content=f"Server error: {str(e)}", status_code=500)
        
    except subprocess.CalledProcessError as e:
        return Response(content=f"Processing failed: {str(e)}", status_code=500)
    finally:
        # 6. Clean up temporary files
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)