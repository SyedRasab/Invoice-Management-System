import os
import zipfile
import shutil

def zip_project():
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(project_root, 'deployment_package.zip')
    
    print(f"Zipping project to: {output_filename}")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through backend
        backend_dir = os.path.join(project_root, 'backend')
        for root, dirs, files in os.walk(backend_dir):
            if '__pycache__' in root or 'venv' in root or '.git' in root:
                continue
                
            for file in files:
                if file.endswith('.pyc') or file == 'invoice_system.db': # Don't ship local DB if we want fresh
                    continue
                    
                file_path = os.path.join(root, file)
                # Calculate relative path for archive
                arcname = os.path.relpath(file_path, project_root)
                zipf.write(file_path, arcname)
                
        # Walk through frontend
        frontend_dir = os.path.join(project_root, 'frontend')
        for root, dirs, files in os.walk(frontend_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_root)
                zipf.write(file_path, arcname)
                
    print("Deployment package created successfully!")

if __name__ == '__main__':
    zip_project()
