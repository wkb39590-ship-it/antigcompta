import psycopg2
import sys

def restore():
    conn_str = "postgresql+psycopg2://postgres:admin@127.0.0.1:5432/compta_db"
    # Convert sqlalchemy style to psycopg2 style
    conn_str = conn_str.replace("+psycopg2", "")
    
    try:
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Lecture du fichier de sauvegarde...")
        with open('backup_compta_db_complete.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # On va essayer de l'exécuter par blocs ou d'un coup
        # Attention: les dumps pg_dump peuvent être complexes (COPY stdin)
        # Il est préférable d'utiliser psql si possible.
        # Mais essayons l'exécution directe si psql manque.
        
        print("Début de la restauration...")
        cur.execute(sql)
        print("Restauration terminée avec succès !")
        
    except Exception as e:
        print(f"Erreur lors de la restauration : {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    restore()
