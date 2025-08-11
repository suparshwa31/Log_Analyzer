import os
import uuid
from typing import Optional
from werkzeug.datastructures import FileStorage
from supabase import create_client, Client
from config import Config

class FileStorageManager:
    """Manages file storage operations for local and Supabase"""
    
    def __init__(self):
        self.config = Config()
        self.supabase_client: Optional[Client] = None
        self.use_supabase = bool(self.config.SUPABASE_URL and self.config.SUPABASE_SERVICE_ROLE_KEY)
        
        if self.use_supabase:
            try:
                self.supabase_client = create_client(
                    self.config.SUPABASE_URL,
                    self.config.SUPABASE_SERVICE_ROLE_KEY
                )
            except Exception as e:
                self.use_supabase = False
    
    def save_file(self, file: FileStorage, filename: str, user_id: Optional[str] = None) -> str:
        """Save file to storage and return file path/identifier"""
        if self.use_supabase and user_id:
            return self._save_to_supabase(file, filename, user_id)
        else:
            return self._save_to_local(file, filename)
    
    def _save_to_local(self, file: FileStorage, filename: str) -> str:
        """Save file to local storage"""
        # Ensure upload directory exists
        os.makedirs(self.config.UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.config.UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        return file_path
    
    def _save_to_supabase(self, file: FileStorage, filename: str, user_id: str) -> str:
        """Save file to Supabase storage"""
        try:
            if not self.supabase_client:
                raise Exception("Supabase client not initialized")
            
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{user_id}/{uuid.uuid4()}{file_extension}"
            
            # Upload to Supabase storage
            file_content = file.read()
            bucket_name = self.config.SUPABASE_BUCKET
            
            result = self.supabase_client.storage.from_(bucket_name).upload(
                unique_filename,
                file_content,
                {'content-type': file.content_type}
            )
            
            # Return the file identifier
            return f"supabase://{bucket_name}/{unique_filename}"
            
        except Exception as e:
            # Fallback to local storage if Supabase fails
            return self._save_to_local(file, filename)
    
    def get_file(self, file_identifier: str) -> Optional[bytes]:
        """Retrieve file content from storage"""
        if file_identifier.startswith('supabase://'):
            return self._get_from_supabase(file_identifier)
        else:
            return self._get_from_local(file_identifier)
    
    def _get_from_local(self, file_path: str) -> Optional[bytes]:
        """Retrieve file from local storage"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
        except Exception:
            pass
        return None
    
    def _get_from_supabase(self, file_identifier: str) -> Optional[bytes]:
        """Retrieve file from Supabase storage"""
        try:
            if not self.supabase_client:
                return None
            
            # Extract path from identifier
            bucket_name = self.config.SUPABASE_BUCKET
            path = file_identifier.replace(f'supabase://{bucket_name}/', '')
            
            # Download from Supabase
            result = self.supabase_client.storage.from_(bucket_name).download(path)
            return result
            
        except Exception as e:
            return None
    
    def delete_file(self, file_identifier: str) -> bool:
        """Delete file from storage"""
        if file_identifier.startswith('supabase://'):
            return self._delete_from_supabase(file_identifier)
        else:
            return self._delete_from_local(file_identifier)
    
    def _delete_from_local(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
    
    def _delete_from_supabase(self, file_identifier: str) -> bool:
        """Delete file from Supabase storage"""
        try:
            if not self.supabase_client:
                return False
            
            # Extract path from identifier
            bucket_name = self.config.SUPABASE_BUCKET
            path = file_identifier.replace(f'supabase://{bucket_name}/', '')
            
            # Delete from Supabase
            self.supabase_client.storage.from_(bucket_name).remove([path])
            return True
            
        except Exception as e:
            return False
    
    def list_files(self, user_id: Optional[str] = None) -> list:
        """List files in storage"""
        if self.use_supabase and user_id:
            return self._list_from_supabase(user_id)
        else:
            return self._list_from_local()
    
    def _list_from_local(self) -> list:
        """List files from local storage"""
        files = []
        try:
            if os.path.exists(self.config.UPLOAD_FOLDER):
                for filename in os.listdir(self.config.UPLOAD_FOLDER):
                    file_path = os.path.join(self.config.UPLOAD_FOLDER, filename)
                    if os.path.isfile(file_path):
                        try:
                            stat = os.stat(file_path)
                            files.append({
                                'filename': filename,
                                'size': stat.st_size,
                                'created_at': float(stat.st_ctime),  # Ensure it's a float
                                'path': file_path
                            })
                        except Exception as e:
                            continue
        except Exception as e:
            pass
        return files
    
    def _list_from_supabase(self, user_id: str) -> list:
        """List files from Supabase storage"""
        try:
            if not self.supabase_client:
                return []
            
            bucket_name = self.config.SUPABASE_BUCKET
            # List files in user's folder
            result = self.supabase_client.storage.from_(bucket_name).list(user_id)
            files = []
            
            for file_info in result:
                try:
                    # Parse timestamp if it's a string, otherwise default to current time
                    created_at = file_info.get('created_at', 0)
                    if isinstance(created_at, str):
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_at = dt.timestamp()
                    elif created_at is None:
                        created_at = 0
                    
                    files.append({
                        'filename': file_info['name'],
                        'size': file_info.get('metadata', {}).get('size', 0),
                        'created_at': float(created_at),
                        'path': f"supabase://{bucket_name}/{user_id}/{file_info['name']}"
                    })
                except Exception as e:
                    print(f"Error processing Supabase file {file_info.get('name', 'unknown')}: {e}")
                    continue
            
            return files
            
        except Exception as e:
            print(f"Supabase list failed: {e}")
            return []

# Global instance
file_storage = FileStorageManager()

def save_file(file: FileStorage, filename: str, user_id: Optional[str] = None) -> str:
    """Convenience function to save a file"""
    return file_storage.save_file(file, filename, user_id)

def get_file(file_identifier: str) -> Optional[bytes]:
    """Convenience function to get a file"""
    return file_storage.get_file(file_identifier)

def delete_file(file_identifier: str) -> bool:
    """Convenience function to delete a file"""
    return file_storage.delete_file(file_identifier)
