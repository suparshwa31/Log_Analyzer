import os
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional

class Config(BaseSettings):
    # Flask Configuration
    debug: bool = Field(default=False, alias='FLASK_ENV')
    
    # Supabase Configuration
    supabase_url: str = Field(..., alias='SUPABASE_URL')
    supabase_anon_key: str = Field(..., alias='SUPABASE_ANON_KEY')
    supabase_service_role_key: str = Field(..., alias='SUPABASE_SERVICE_ROLE_KEY')
    supabase_bucket: str = Field(..., alias='SUPABASE_BUCKET')
    
    # File Upload Configuration
    max_content_length: int = Field(default=50 * 1024 * 1024, alias='MAX_CONTENT_LENGTH')  # 50MB
    upload_folder: str = Field(default='uploads', alias='UPLOAD_FOLDER')
    allowed_extensions: List[str] = Field(default=['log', 'txt', 'gz', 'tar'], alias='ALLOWED_EXTENSIONS')
    
    # Log Analysis Configuration
    max_log_size: int = Field(default=50 * 1024 * 1024, alias='MAX_LOG_SIZE')  # 50MB
    
    # AI/LLM Configuration (optional)
    openai_api_key: Optional[str] = Field(default=None, alias='OPENAI_API_KEY')
    
    # Development Configuration
    host: str = Field(default='0.0.0.0', alias='HOST')
    port: int = Field(default=5001, alias='PORT')
    
    @validator('max_content_length', 'max_log_size')
    def validate_positive_size(cls, v):
        if v <= 0:
            raise ValueError('Size must be positive')
        return v
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @property
    def DEBUG(self) -> bool:
        return self.debug
    
    @property
    def SUPABASE_URL(self) -> str:
        return self.supabase_url
    
    @property
    def SUPABASE_ANON_KEY(self) -> str:
        return self.supabase_anon_key
    
    @property
    def SUPABASE_SERVICE_ROLE_KEY(self) -> str:
        return self.supabase_service_role_key
    
    @property
    def SUPABASE_BUCKET(self) -> str:
        return self.supabase_bucket
    
    @property
    def MAX_CONTENT_LENGTH(self) -> int:
        return self.max_content_length
    
    @property
    def UPLOAD_FOLDER(self) -> str:
        # Ensure absolute path
        if os.path.isabs(self.upload_folder):
            return self.upload_folder
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), self.upload_folder)
    
    @property
    def ALLOWED_EXTENSIONS(self) -> set:
        return set(self.allowed_extensions)
    
    @property
    def MAX_LOG_SIZE(self) -> int:
        return self.max_log_size
    
    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        return self.openai_api_key
    
    @property
    def HOST(self) -> str:
        return self.host
    
    @property
    def PORT(self) -> int:
        return self.port
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
    
    def init_app(self, app):
        # Ensure upload directory exists
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
