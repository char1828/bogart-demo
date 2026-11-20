import time
from typing import List, Dict, Any, Optional, Tuple
from database.connection import db_manager

class MediaRepository:
    def __init__(self):
        self.mgr = db_manager

    # --------------------------------------------------------------------------
    # Option 1: Database BLOB Operations
    # --------------------------------------------------------------------------
    def get_records_option1(self) -> List[Dict[str, Any]]:
        conn = self.mgr.get_connection()
        db_type = self.mgr.db_cfg.type.lower()
        query = """
            SELECT id, name, img_id, size, img_type, created_at
            FROM media_blob_store
            ORDER BY id ASC
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            
            if hasattr(conn, 'row_factory') and conn.row_factory: # SQLite
                return [dict(row) for row in cursor.fetchall()]
            
            # pg8000 or generic DB-API
            cols = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(cols, row)) for row in rows]
        finally:
            conn.close()

    def get_image_blob_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        conn = self.mgr.get_connection()
        db_type = self.mgr.db_cfg.type.lower()
        
        query = "SELECT id, name, img_id, size, img_type, img_data FROM media_blob_store WHERE id = ?"
        if "postgres" in db_type or "mysql" in db_type or "mssql" in db_type:
            query = query.replace("?", "%s")

        try:
            cursor = conn.cursor()
            cursor.execute(query, (record_id,))
            
            if hasattr(conn, 'row_factory') and conn.row_factory: # SQLite
                res = cursor.fetchone()
                return dict(res) if res else None
            
            cols = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            if not row:
                return None
            result = dict(zip(cols, row))
            # Ensure img_data is bytes
            if isinstance(result.get("img_data"), memoryview):
                result["img_data"] = result["img_data"].tobytes()
            return result
        finally:
            conn.close()

    def insert_record_option1(self, name: str, img_id: str, size: int, img_type: str, img_data: bytes) -> int:
        conn = self.mgr.get_connection()
        db_type = self.mgr.db_cfg.type.lower()

        if "postgres" in db_type:
            query = """
                INSERT INTO media_blob_store (name, img_id, size, img_type, img_data)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            try:
                import pg8000
                cursor = conn.cursor()
                cursor.execute(query, (name, img_id, size, img_type, pg8000.Binary(img_data)))
                row_id = cursor.fetchone()[0]
                conn.commit()
                return row_id
            finally:
                conn.close()

        else:
            query = """
                INSERT INTO media_blob_store (name, img_id, size, img_type, img_data)
                VALUES (?, ?, ?, ?, ?)
            """
            if "mysql" in db_type or "mssql" in db_type:
                query = query.replace("?", "%s")

            try:
                cursor = conn.cursor()
                cursor.execute(query, (name, img_id, size, img_type, img_data))
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()

    # --------------------------------------------------------------------------
    # Option 2: Hybrid Object Storage Operations
    # --------------------------------------------------------------------------
    def get_records_option2(self) -> List[Dict[str, Any]]:
        conn = self.mgr.get_connection()
        query = """
            SELECT id, name, img_id, size, img_type, img_Path, created_at
            FROM media_metadata_store
            ORDER BY id ASC
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            
            if hasattr(conn, 'row_factory') and conn.row_factory: # SQLite
                return [dict(row) for row in cursor.fetchall()]
            
            cols = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(cols, row)) for row in rows]
        finally:
            conn.close()

    def get_image_path_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        conn = self.mgr.get_connection()
        db_type = self.mgr.db_cfg.type.lower()
        
        query = "SELECT id, name, img_id, size, img_type, img_Path FROM media_metadata_store WHERE id = ?"
        if "postgres" in db_type or "mysql" in db_type or "mssql" in db_type:
            query = query.replace("?", "%s")

        try:
            cursor = conn.cursor()
            cursor.execute(query, (record_id,))
            
            if hasattr(conn, 'row_factory') and conn.row_factory: # SQLite
                res = cursor.fetchone()
                return dict(res) if res else None
            
            cols = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            if not row:
                return None
            return dict(zip(cols, row))
        finally:
            conn.close()

    def insert_record_option2(self, name: str, img_id: str, size: int, img_type: str, img_path: str) -> int:
        conn = self.mgr.get_connection()
        db_type = self.mgr.db_cfg.type.lower()

        if "postgres" in db_type:
            query = """
                INSERT INTO media_metadata_store (name, img_id, size, img_type, img_Path)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            try:
                cursor = conn.cursor()
                cursor.execute(query, (name, img_id, size, img_type, img_path))
                row_id = cursor.fetchone()[0]
                conn.commit()
                return row_id
            finally:
                conn.close()

        else:
            query = """
                INSERT INTO media_metadata_store (name, img_id, size, img_type, img_Path)
                VALUES (?, ?, ?, ?, ?)
            """
            if "mysql" in db_type or "mssql" in db_type:
                query = query.replace("?", "%s")

            try:
                cursor = conn.cursor()
                cursor.execute(query, (name, img_id, size, img_type, img_path))
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()

    def get_counts(self) -> Dict[str, int]:
        conn = self.mgr.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM media_blob_store")
            c1 = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM media_metadata_store")
            c2 = cursor.fetchone()[0]
            return {"option1_blob_count": c1, "option2_meta_count": c2}
        except Exception:
            return {"option1_blob_count": 0, "option2_meta_count": 0}
        finally:
            conn.close()

    def clear_all(self):
        conn = self.mgr.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM media_blob_store")
            cursor.execute("DELETE FROM media_metadata_store")
            conn.commit()
        finally:
            conn.close()

media_repo = MediaRepository()
