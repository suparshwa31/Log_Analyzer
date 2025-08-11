from flask import Blueprint, request, jsonify
from utils.security import validate_jwt_token
from models.schemas import AuthResponse, UserResponse, ErrorResponse
from functools import wraps
from pydantic import ValidationError

auth_bp = Blueprint('auth', __name__)

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            error_response = ErrorResponse(
                error='No authorization header',
                details='Authorization header is required'
            )
            return jsonify(error_response.model_dump()), 401
        
        token = auth_header.replace('Bearer ', '')
        try:
            user = validate_jwt_token(token)
            request.user = user
            return f(*args, **kwargs)
        except Exception as e:
            error_response = ErrorResponse(
                error='Invalid token',
                details=str(e)
            )
            return jsonify(error_response.model_dump()), 401
    
    return decorated_function

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT token and return user info"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        error_response = ErrorResponse(
            error='No authorization header',
            details='Authorization header is required'
        )
        return jsonify(error_response.model_dump()), 401
    
    token = auth_header.replace('Bearer ', '')
    try:
        user = validate_jwt_token(token)
        auth_response = AuthResponse(
            valid=True,
            user=UserResponse(
                id=user.get('id', ''),
                email=user.get('email', ''),
                role=user.get('role', 'user'),
                provider=user.get('provider', 'unknown')
            )
        )
        return jsonify(auth_response.model_dump())
    except Exception as e:
        auth_response = AuthResponse(
            valid=False,
            error=str(e)
        )
        return jsonify(auth_response.model_dump()), 401

@auth_bp.route('/user', methods=['GET'])
@require_auth
def get_user_info():
    """Get current user information"""
    try:
        user_response = UserResponse(
            id=request.user.get('id', ''),
            email=request.user.get('email', ''),
            role=request.user.get('role', 'user'),
            provider=request.user.get('provider', 'unknown')
        )
        return jsonify({'user': user_response.model_dump()})
    except ValidationError as e:
        error_response = ErrorResponse(
            error='Invalid user data',
            details=str(e.errors())
        )
        return jsonify(error_response.model_dump()), 500
