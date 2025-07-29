# erp/migrate_from_databricks.py

import os
import pandas as pd
from databricks import sql
import psycopg2
from psycopg2 import extras # Per execute_batch
from dotenv import load_dotenv

load_dotenv()

# --- Configurazione Generale ---
DATABRICKS_SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DATABRICKS_ACCESS_TOKEN = os.getenv("DATABRICKS_ACCESS_TOKEN")
POSTGRES_DB_URL = os.getenv("DATABASE_URL")

# --- Mappa delle configurazioni per ogni tabella ---
TABLE_CONFIGS = {
    "fornitore": { # Chiave: un nome interno descrittivo
        "databricks_full_table_name": "mf_dbs.gold_layer.fornitore", # Percorso completo della tabella in Databricks
        "postgres_table_name": "reorder_system_fornitore", # Nome tabella Django generato (appname_modelname)
        "databricks_columns_to_select": [ # Colonne ESATTE da selezionare da Databricks (nell'ordine)
            "IDFornitore", "Nome", "Indirizzo", "Cap", "Citta", "Prov", "Nazione", "Tel", "Cell",
            "Email", "CodiceFiscale", "PartitaIva", "Note", "Idata", "Paga",
            "ordinetot", "minio" # 'minio' è il nome della colonna in Databricks
        ],
        "column_rename_map": { # Mappa per rinominare da Databricks a Django
            'IDFornitore': 'id_fornitore_databricks',
            'Nome': 'nome',
            'Indirizzo': 'indirizzo',
            'Cap': 'cap',
            'Citta': 'citta',
            'Prov': 'prov',
            'Nazione': 'nazione',
            'Tel': 'tel',
            'Cell': 'cell',
            'Email': 'email',
            'CodiceFiscale': 'codicefiscale',
            'PartitaIva': 'partitaiva',
            'Note': 'note',
            'Idata': 'idata',
            'Paga': 'paga',
            'ordinetot': 'ordinetot',
            'minio': 'minimo' # Rinomina 'minio' di Databricks a 'minimo' per il modello Django
        },
        "django_model_columns_order": [ # Nomi dei campi nel modello Django (nell'ordine per l'inserimento)
            'id_fornitore_databricks', 'nome', 'indirizzo', 'cap', 'citta', 'prov', 'nazione',
            'tel', 'cell', 'email', 'codicefiscale', 'partitaiva', 'note', 'idata',
            'paga', 'ordinetot', 'minimo'
        ]
    }
    # Aggiungi qui altre configurazioni di tabelle quando sarai pronto, ad esempio per 'prodotti'
}


def extract_from_databricks(databricks_full_table_name, databricks_columns_to_select):
    """Estrae i dati dalla tabella specificata in Databricks."""
    if not all([DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH, DATABRICKS_ACCESS_TOKEN]):
        print("Errore: Variabili d'ambiente per Databricks non impostate correttamente.")
        print("Assicurati di avere DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH, DATABRICKS_ACCESS_TOKEN nel tuo .env.")
        return None

    try:
        with sql.connect(
            server_hostname=DATABRICKS_SERVER_HOSTNAME,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_ACCESS_TOKEN
        ) as connection:
            with connection.cursor() as cursor:
                columns_to_select_str = ", ".join(databricks_columns_to_select)
                query = f"SELECT {columns_to_select_str} FROM {databricks_full_table_name}"
                print(f"Esecuzione query Databricks: {query}")
                cursor.execute(query)
                rows = cursor.fetchall()

                # Usa i nomi delle colonne esattamente come selezionati da Databricks
                df = pd.DataFrame(rows, columns=databricks_columns_to_select)
                print(f"Estratti {len(df)} righe da {databricks_full_table_name}.")
                return df
    except Exception as e:
        print(f"Errore durante l'estrazione da Databricks per {databricks_full_table_name}: {e}")
        return None

def transform_data(df, column_rename_map, django_model_columns_order):
    """Esegue trasformazioni e rinominazioni sui dati per allinearli al modello Django."""
    if df is None:
        return None

    # Applica la rinominazione delle colonne
    df = df.rename(columns=column_rename_map)

    # Riordina e filtra le colonne per corrispondere ESATTAMENTE ai campi del modello Django
    # In questo modo, l'ordine delle colonne nel DF sarà lo stesso dei campi del modello Django,
    # il che è fondamentale per l'inserimento batch tramite psycopg2.extras.execute_batch
    final_columns_for_insert = []
    for col_name in django_model_columns_order:
        if col_name in df.columns:
            final_columns_for_insert.append(col_name)
        else:
            # Se un campo del modello Django non è presente nel DataFrame dopo le trasformazioni,
            # puoi decidere come gestirlo:
            # 1. Inserire None (se il campo nel modello è null=True)
            # 2. Assegnare un valore di default
            # Per ora, aggiungiamo una colonna con None per i campi mancanti nel DF ma presenti nel modello
            df[col_name] = None
            final_columns_for_insert.append(col_name) # Aggiungi anche se appena creata

    # Riordina il DataFrame per l'inserimento
    df = df[final_columns_for_insert]

    print("Dati trasformati e colonne riordinate per l'inserimento.")
    return df

def load_to_postgres(df, postgres_table_name):
    """Carica i dati trasformati nel database PostgreSQL."""
    if df is None or df.empty:
        print(f"Nessun dato da caricare nella tabella {postgres_table_name}.")
        return

    if not POSTGRES_DB_URL:
        print("Errore: Variabile d'ambiente DATABASE_URL per PostgreSQL non impostata.")
        return

    try:
        conn = psycopg2.connect(POSTGRES_DB_URL)
        cur = conn.cursor()

        # Prepara la query di inserimento usando i nomi delle colonne finali dal DataFrame
        # che ora corrispondono ai nomi dei campi del modello Django
        columns_for_insert = ', '.join(df.columns)
        values_placeholder = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO {postgres_table_name} ({columns_for_insert}) VALUES ({values_placeholder}) ON CONFLICT (id_fornitore_databricks) DO NOTHING;"
        # Ho aggiunto ON CONFLICT DO NOTHING sul campo unico 'id_fornitore_databricks'
        # Questo previene errori se esegui lo script più volte e trovi duplicati.

        extras.execute_batch(cur, insert_query, df.values.tolist())

        conn.commit()
        cur.close()
        conn.close()
        print(f"Caricate {len(df)} righe nella tabella {postgres_table_name} in PostgreSQL.")
    except Exception as e:
        print(f"Errore durante il caricamento in PostgreSQL per {postgres_table_name}: {e}")

if __name__ == "__main__":
    print("Inizio processo di migrazione dati da Databricks a PostgreSQL per la tabella 'fornitore'...")

    # Esegui la migrazione solo per il fornitore
    fornitore_config = TABLE_CONFIGS["fornitore"]

    # 1. Estrai i dati
    data_df = extract_from_databricks(
        fornitore_config["databricks_full_table_name"],
        fornitore_config["databricks_columns_to_select"]
    )

    if data_df is not None:
        # 2. Trasforma i dati
        transformed_df = transform_data(
            data_df,
            fornitore_config["column_rename_map"],
            fornitore_config["django_model_columns_order"]
        )

        # 3. Carica i dati in PostgreSQL
        load_to_postgres(transformed_df, fornitore_config["postgres_table_name"])

    print("\nProcesso di migrazione dati completato per 'fornitore'.")