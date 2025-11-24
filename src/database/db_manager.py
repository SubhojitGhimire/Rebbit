import sqlite3
from src.utils.config import Config

class DBManager:
    def __init__(self):
        self.db_path = Config.BASE_DIR / "data" / "rebbit.db"
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON") 
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                artist TEXT,
                album TEXT,
                filepath TEXT UNIQUE,
                cover_path TEXT,
                duration INTEGER,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_songs (
                playlist_id INTEGER,
                song_id INTEGER,
                FOREIGN KEY(playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY(song_id) REFERENCES songs(id) ON DELETE CASCADE,
                PRIMARY KEY (playlist_id, song_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_song(self, song_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO songs (title, artist, album, filepath, cover_path, duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                song_data.get('title'),
                song_data.get('artist'),
                song_data.get('album'),
                song_data.get('filepath'),
                song_data.get('cover_path'),
                song_data.get('duration')
            ))
            conn.commit()
        except Exception as e:
            print(f"DB Error: {e}")
        finally:
            conn.close()

    def get_all_songs(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM songs ORDER BY title ASC')
        songs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return songs

    def song_exists(self, filepath):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM songs WHERE filepath = ?', (filepath,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def create_playlist(self, name):
        conn = self.get_connection()
        try:
            conn.execute('INSERT INTO playlists (name) VALUES (?)', (name,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False 
        finally:
            conn.close()

    def get_playlists(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, COUNT(ps.song_id) as song_count 
            FROM playlists p 
            LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id 
            GROUP BY p.id
        ''')
        playlists = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return playlists

    def add_to_playlist(self, playlist_id, song_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM songs WHERE filepath = ?', (song_path,))
        res = cursor.fetchone()
        if res:
            song_id = res['id']
            try:
                cursor.execute('INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)', (playlist_id, song_id))
                conn.commit()
            except sqlite3.IntegrityError:
                pass 
        conn.close()

    def get_playlist_songs(self, playlist_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.* FROM songs s
            JOIN playlist_songs ps ON s.id = ps.song_id
            WHERE ps.playlist_id = ?
        ''', (playlist_id,))
        songs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return songs
        
    def rename_playlist(self, playlist_id, new_name):
        conn = self.get_connection()
        try:
            conn.execute('UPDATE playlists SET name = ? WHERE id = ?', (new_name, playlist_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False 
        finally:
            conn.close()

    def delete_playlist(self, playlist_id):
        conn = self.get_connection()
        conn.execute('DELETE FROM playlists WHERE id = ?', (playlist_id,))
        conn.commit()
        conn.close()

    def remove_from_playlist(self, playlist_id, song_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM songs WHERE filepath = ?', (song_path,))
        res = cursor.fetchone()
        if res:
            song_id = res['id']
            conn.execute('DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?', (playlist_id, song_id))
            conn.commit()
        conn.close()
    
    def update_song_metadata(self, song_id, title, artist, album, cover_path, new_filepath=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if new_filepath:
                cursor.execute('''
                    UPDATE songs 
                    SET title = ?, artist = ?, album = ?, cover_path = ?, filepath = ?
                    WHERE id = ?
                ''', (title, artist, album, cover_path, new_filepath, song_id))
            else:
                cursor.execute('''
                    UPDATE songs 
                    SET title = ?, artist = ?, album = ?, cover_path = ?
                    WHERE id = ?
                ''', (title, artist, album, cover_path, song_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"DB Update Error: {e}")
            return False
        finally:
            conn.close()

