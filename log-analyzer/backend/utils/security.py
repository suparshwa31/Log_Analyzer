import jwt
import requests
from typing import Dict, Any, Optional
from supabase import create_client, Client
from config import Config

class SecurityManager:
    """Manages authentication and security operations"""
    
    def __init__(self):
        self._config = None
        self.supabase_client: Optional[Client] = None
    
    @property
    def config(self):
        """Lazy load config to avoid import errors"""
        if self._config is None:
            try:
                self._config = Config()
            except Exception as e:
                # If config fails to load, create a minimal config for development
                self._config = type('MockConfig', (), {
                    'SUPABASE_URL': None,
                    'SUPABASE_ANON_KEY': None
                })()
        return self._config
    
    def _init_supabase_client(self):
        """Initialize Supabase client if not already done"""
        if self.supabase_client is None and self.config.SUPABASE_URL and self.config.SUPABASE_SERVICE_ROLE_KEY:
            try:
                self.supabase_client = create_client(
                    self.config.SUPABASE_URL,
                    self.config.SUPABASE_SERVICE_ROLE_KEY
                )
            except Exception:
                pass
    
    def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return user information"""
        try:
            # Initialize Supabase client if needed
            self._init_supabase_client()
            
            # First try to validate with Supabase
            if self.supabase_client:
                try:
                    user = self.supabase_client.auth.get_user(token)
                    if user and user.user:
                        return {
                            'id': user.user.id,
                            'email': user.user.email,
                            'role': 'user',
                            'provider': 'supabase'
                        }
                except Exception as e:
                    pass
            
            # Fallback to manual JWT validation
            return self._validate_jwt_manually(token)
            
        except Exception as e:
            raise Exception(f"Token validation failed: {str(e)}")
    
    def _validate_jwt_manually(self, token: str) -> Dict[str, Any]:
        """Manual JWT validation as fallback"""
        try:
            # Decode JWT without verification (for development)
            # In production, you should verify the signature
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Extract user information
            user_id = payload.get('sub') or payload.get('user_id')
            email = payload.get('email')
            
            if not user_id:
                raise Exception("Invalid token payload")
            
            return {
                'id': user_id,
                'email': email,
                'role': payload.get('role', 'user'),
                'provider': 'jwt'
            }
            
        except jwt.InvalidTokenError as e:
            raise Exception(f"Invalid JWT token: {str(e)}")
    
    def verify_supabase_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify token specifically with Supabase"""
        self._init_supabase_client()
        
        if not self.supabase_client:
            return None
        
        try:
            # Get user from Supabase
            user = self.supabase_client.auth.get_user(token)
            
            if user and user.user:
                return {
                    'id': user.user.id,
                    'email': user.user.email,
                    'role': 'user',
                    'provider': 'supabase'
                }
            
            return None
            
        except Exception:
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh an expired access token"""
        self._init_supabase_client()
        
        if not self.supabase_client:
            return None
        
        try:
            # Refresh token with Supabase
            response = self.supabase_client.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    'access_token': response.session.access_token,
                    'refresh_token': response.session.refresh_token,
                    'expires_at': response.session.expires_at
                }
            
            return None
            
        except Exception:
            return None
    
    def validate_permissions(self, user: Dict[str, Any], required_permission: str) -> bool:
        """Validate if user has required permission"""
        # Basic permission checking
        user_role = user.get('role', 'user')
        
        # Define permission hierarchy
        permissions = {
            'admin': ['read', 'write', 'delete', 'admin'],
            'user': ['read', 'write'],
            'guest': ['read']
        }
        
        user_permissions = permissions.get(user_role, [])
        return required_permission in user_permissions
    
    def sanitize_input(self, input_data: str) -> str:
        """Basic input sanitization"""
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')']
        sanitized = input_data
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    def validate_file_type(self, filename: str, allowed_types: set) -> bool:
        """Validate file type based on extension"""
        if not filename or '.' not in filename:
            return False
        
        file_extension = filename.rsplit('.', 1)[1].lower()
        return file_extension in allowed_types
    
    def validate_file_size(self, file_size: int, max_size: int) -> bool:
        """Validate file size"""
        return file_size <= max_size
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """Generate a secure filename"""
        import uuid
        import os
        
        # Get file extension
        file_extension = os.path.splitext(original_filename)[1]
        
        # Generate unique filename
        secure_filename = f"{uuid.uuid4()}{file_extension}"
        
        return secure_filename

# Global instance
security_manager = SecurityManager()

def validate_jwt_token(token: str) -> Dict[str, Any]:
    """Convenience function to validate JWT token"""
    return security_manager.validate_jwt_token(token)

def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """Convenience function to verify Supabase token"""
    return security_manager.verify_supabase_token(token)

def validate_permissions(user: Dict[str, Any], required_permission: str) -> bool:
    """Convenience function to validate user permissions"""
    return security_manager.validate_permissions(user, required_permission)
