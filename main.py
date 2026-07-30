from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat

app = FastAPI(title="AI Chatbot Backend")

# CORS - taaki React frontend backend ko call kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production me apne frontend ka exact URL daalna: ["https://yourapp.netlify.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "running"}
