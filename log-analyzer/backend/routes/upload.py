import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from services.parser import LogParser
from utils.file_storage import save_file
from routes.auth import require_auth
from models.schemas import (
    FileInfoResponse, FileListResponse, UploadResponse, 
    DeleteFileResponse, ErrorResponse
)
from pydantic import ValidationError

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route('/file', methods=['POST'])
@require_auth
def upload_file():
    """Handle file upload and initial parsing"""
    if 'file' not in request.files:
        error_response = ErrorResponse(
            error='No file part',
            details='File field is required in the request'
        )
        return jsonify(error_response.model_dump()), 400
    
    file = request.files['file']
    if file.filename == '':
        error_response = ErrorResponse(
            error='No selected file',
            details='Please select a file to upload'
        )
        return jsonify(error_response.model_dump()), 400
    
    if file and allowed_file(file.filename):
        try:
            # Get user ID from authenticated request
            user_id = request.user.get('id', 'anonymous')
            
            # Save file (will use Supabase if configured, otherwise local)
            filename = secure_filename(file.filename)
            file_path = save_file(file, filename, user_id)
            
            # Parse log file
            parser = LogParser()
            parse_result = parser.parse_file(file_path)
            
            upload_response = UploadResponse(
                message='File uploaded and parsed successfully',
                filename=filename,
                file_path=file_path,
                parse_result=parse_result
            )
            
            return jsonify(upload_response.model_dump())
            
        except Exception as e:
            error_response = ErrorResponse(
                error='Error processing file',
                details=str(e)
            )
            return jsonify(error_response.model_dump()), 500
    
    error_response = ErrorResponse(
        error='File type not allowed',
        details=f'Allowed types: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'
    )
    return jsonify(error_response.model_dump()), 400

@upload_bp.route('/files', methods=['GET'])
@require_auth
def list_uploaded_files():
    """List all uploaded files for the user"""
    try:
        # Get user ID from authenticated request
        user_id = request.user.get('id', 'anonymous')
        
        # Use file storage manager to list files
        from utils.file_storage import file_storage
        files_data = file_storage.list_files(user_id)
        
        # Convert to FileInfoResponse objects
        files = []
        for file_data in files_data:
            try:
                file_info = FileInfoResponse(
                    filename=file_data['filename'],
                    size=file_data['size'],
                    uploaded_at=float(file_data['created_at']),  # Ensure it's a float
                    path=file_data.get('path')
                )
                files.append(file_info)
            except Exception as file_error:
                continue
        
        file_list_response = FileListResponse(files=files)
        return jsonify(file_list_response.model_dump())
        
    except Exception as e:
        error_response = ErrorResponse(
            error='Error listing files',
            details=str(e)
        )
        return jsonify(error_response.model_dump()), 500


@upload_bp.route('/file/<filename>', methods=['DELETE'])
@require_auth
def delete_file(filename):
    """Delete an uploaded file"""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, secure_filename(filename))
        
        if os.path.exists(file_path):
            os.remove(file_path)
            delete_response = DeleteFileResponse(
                message=f'File {filename} deleted successfully'
            )
            return jsonify(delete_response.model_dump())
        else:
            error_response = ErrorResponse(
                error='File not found',
                details=f'File {filename} does not exist'
            )
            return jsonify(error_response.model_dump()), 404
            
    except Exception as e:
        error_response = ErrorResponse(
            error='Error deleting file',
            details=str(e)
        )
        return jsonify(error_response.model_dump()), 500
