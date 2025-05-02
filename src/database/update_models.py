#!/usr/bin/env python3
"""
Update database models to fix metadata attribute naming issues.

This script updates the database models to fix issues with the metadata attribute name,
which is a reserved attribute name in SQLAlchemy's Declarative API.
"""

import os
import sys
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("g3r4ki.database.update_models")

def update_models_file():
    """Update the models.py file to fix metadata attribute names."""
    models_file = os.path.join(os.path.dirname(__file__), "models.py")
    
    try:
        with open(models_file, "r") as f:
            content = f.read()
        
        # Replace all occurrences of metadata with meta_data
        updated_content = re.sub(r'metadata\s*=\s*Column\(', 'meta_data = Column(', content)
        
        with open(models_file, "w") as f:
            f.write(updated_content)
        
        logger.info(f"Updated {models_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating models file: {e}")
        return False

def update_operations_file():
    """Update the operations.py file to use meta_data instead of metadata."""
    operations_file = os.path.join(os.path.dirname(__file__), "operations.py")
    
    try:
        with open(operations_file, "r") as f:
            content = f.read()
        
        # Replace in function body where metadata is used to access the database field
        updated_content = re.sub(
            r'activity\.metadata', 
            'activity.meta_data', 
            content
        )
        
        updated_content = re.sub(
            r'file_record\.metadata', 
            'file_record.meta_data', 
            updated_content
        )
        
        updated_content = re.sub(
            r'credential\.metadata', 
            'credential.meta_data', 
            updated_content
        )
        
        # Replace in Activity creation
        updated_content = re.sub(
            r'metadata=json\.dumps\(metadata\)', 
            'meta_data=json.dumps(metadata)', 
            updated_content
        )
        
        # Write back to file
        with open(operations_file, "w") as f:
            f.write(updated_content)
        
        logger.info(f"Updated {operations_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating operations file: {e}")
        return False

def main():
    """Main function."""
    # Update models file
    if not update_models_file():
        return 1
    
    # Update operations file
    if not update_operations_file():
        return 1
    
    logger.info("Database model updates completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())