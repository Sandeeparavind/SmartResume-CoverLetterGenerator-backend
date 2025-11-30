from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    hf_api_key: str
    hf_model_id: str = "mistralai/Mistral-7B-Instruct-v0.2"  

    class Config:
        env_file = ".env"

settings = Settings()
