from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, List
import os
from urllib.parse import quote

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # Application
    app_name: str = "RAG Retrieval Service"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL") 
    debug: bool = Field(default=False, alias="DEBUG")

    # API
    api_prefix: str = "/api/v1"
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    allowed_hosts: str = Field(default="localhost,127.0.0.1", alias="ALLOWED_HOSTS")

    # OpenAI
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    embedding_model: str = "text-embedding-3-large"
    embedding_dim: int = 3072
    openai_timeout: int = 60

    # Auth
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_audience: Optional[str] = Field(default=None, alias="JWT_AUDIENCE")
    jwt_issuer: Optional[str] = Field(default=None, alias="JWT_ISSUER")

    # Database
    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., alias="POSTGRES_DB")
    postgres_host: str = Field(..., alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    
    # Redis
    redis_host: str = Field(..., alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    redis_ssl: bool = Field(default=False, alias="REDIS_SSL")
    
    @property
    def database_url(self) -> str:
        """Construct DATABASE_URL from individual components."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Construct REDIS_URL from individual components."""
        # Build base URL
        protocol = "rediss" if self.redis_ssl else "redis"
        
        # Add authentication if password exists
        if self.redis_password:
            auth = f":{quote(self.redis_password, safe='')}@"
        else:
            auth = ""
        
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def cors_origin_list(self) -> List[str]:
        if not self.cors_origins or self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def trusted_hosts(self) -> List[str]:
        hosts = [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]
        return hosts or ["localhost", "127.0.0.1"]
    
    # Search Configuration
    enable_bm25: bool = True
    bm25_weight: float = 0.3
    vector_weight: float = 0.7
    
    # Reranking
    jina_api_key: Optional[str] = Field(default=None, alias="JINA_API_KEY")
    reranker_model: str = "jina-reranker-v2-base-multilingual"
    
    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 100
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Zendesk Integration (optional, for import scripts)
    zendesk_subdomain: Optional[str] = Field(default=None, alias="ZENDESK_SUBDOMAIN")
    zendesk_email: Optional[str] = Field(default=None, alias="ZENDESK_EMAIL")
    zendesk_token: Optional[str] = Field(default=None, alias="ZENDESK_TOKEN")

    @property
    def is_docker(self) -> bool:
        return os.path.exists('/.dockerenv')

settings = Settings()
