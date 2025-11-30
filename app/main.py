from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import career

app = FastAPI(title="AI Interview Practice Bot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(career.router)   


@app.get("/health")
def health_check():
    return {"status": "ok"}

# A Schneider Electric Software Engineer job description typically involves designing, developing, and maintaining software for energy management, automation, and sustainability solutions, often requiring skills in languages like C# and .NET Core, and experience with SaaS-based platforms, APIs, and building automation systems. Roles can vary from senior-level positions focused on business-critical applications to more application-based roles involving system integration, customization, and customer support. Common responsibilities include collaborating with cross-functional teams, writing clean code, participating in code reviews, troubleshooting issues, and developing APIs. 
