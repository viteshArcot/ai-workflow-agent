import json
import pandas as pd
from typing import Dict, Any, List
from . import database

class KnowledgeIngestion:
    def ingest_csv(self, file_content: str, filename: str) -> Dict[str, Any]:
        """Ingest CSV content into knowledge base"""
        try:
            # Parse CSV content
            lines = file_content.strip().split('\n')
            if len(lines) < 2:
                raise ValueError("CSV must have at least header and one data row")
            
            # Simple CSV parsing (assumes no commas in values)
            header = [col.strip().strip('"') for col in lines[0].split(',')]
            rows_added = 0
            
            for line in lines[1:]:
                if line.strip():
                    values = [val.strip().strip('"') for val in line.split(',')]
                    if len(values) == len(header):
                        # Create content from row data
                        row_dict = dict(zip(header, values))
                        content = json.dumps(row_dict)
                        metadata = {"source": filename, "type": "csv"}
                        database.add_knowledge(content, metadata)
                        rows_added += 1
            
            return {
                "status": "success",
                "rows_added": rows_added,
                "filename": filename
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "filename": filename
            }
    
    def ingest_json(self, file_content: str, filename: str) -> Dict[str, Any]:
        """Ingest JSON content into knowledge base"""
        try:
            data = json.loads(file_content)
            rows_added = 0
            
            if isinstance(data, list):
                # Array of objects
                for item in data:
                    content = json.dumps(item)
                    metadata = {"source": filename, "type": "json"}
                    database.add_knowledge(content, metadata)
                    rows_added += 1
            elif isinstance(data, dict):
                # Single object
                content = json.dumps(data)
                metadata = {"source": filename, "type": "json"}
                database.add_knowledge(content, metadata)
                rows_added = 1
            else:
                raise ValueError("JSON must be an object or array of objects")
            
            return {
                "status": "success",
                "rows_added": rows_added,
                "filename": filename
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "filename": filename
            }

knowledge_ingestion = KnowledgeIngestion()