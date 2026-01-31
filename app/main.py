from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from modules.auth import sign_up_user, login_user, get_user
from modules.llm import stream_openai, stream_gemini

app = FastAPI(title="Supabase LLM Chatbot API")

class AuthRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    prompt: str
    provider: str = "openai"  # "openai" or "gemini"

@app.post("/signup")
async def signup(request: AuthRequest):
    try:
        response = await sign_up_user(request.email, request.password)
        if response.user:
            return {"message": "User created successfully", "user_id": response.user.id}
        raise HTTPException(status_code=400, detail="Signup failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
async def login(request: AuthRequest):
    try:
        response = await login_user(request.email, request.password)
        if response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user_id": response.user.id
            }
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    try:
        # Verify user with Supabase
        user_res = await get_user(token)
        if not user_res.user:
            raise HTTPException(status_code=401, detail="Invalid session")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if request.provider == "gemini":
        generator = stream_gemini(request.prompt)
    else:
        generator = stream_openai(request.prompt)

    return StreamingResponse(generator, media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
