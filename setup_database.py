import sqlite3
import pandas as pd
import os # To check if files exist

# --- Part 1: Connect to the Database ---
# This is like opening your filing cabinet.
# If 'food_wastage.db' doesn't exist, it will create it.
# If it exists, it will connect to it.
DB_FILE = 'food_wastage.db'
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor() # A cursor is like your hand that does actions inside the database

print(f"--- Connected to {DB_FILE} ---")

# --- Part 2: Create Tables in the Database ---
# Now we'll create the empty "folders" (tables) in our filing cabinet.
# Each folder has specific labels (columns) for the information it holds.

# Table for Food Listings
cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID INTEGER PRIMARY KEY,
        Food_Name TEXT NOT NULL,
        Quantity INTEGER NOT NULL,
        Expiry_Date TEXT NOT NULL, -- Storing as TEXT in YYYY-MM-DD for simplicity
        Provider_ID INTEGER NOT NULL,
        Provider_Type TEXT NOT NULL,
        Location TEXT NOT NULL,
        Food_Type TEXT NOT NULL,
        Meal_Type TEXT NOT NULL
    )
''')

# Table for Providers
cursor.execute('''
    CREATE TABLE IF NOT EXISTS providers (
        Provider_ID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Type TEXT NOT NULL,
        Address TEXT,
        City TEXT NOT NULL,
        Contact TEXT
    )
''')

# Table for Receivers
cursor.execute('''
    CREATE TABLE IF NOT EXISTS receivers (
        Receiver_ID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Type TEXT NOT NULL,
        Address TEXT,
        City TEXT NOT NULL,
        Contact TEXT
    )
''')

# Table for Claims
cursor.execute('''
    CREATE TABLE IF NOT EXISTS claims (
        Claim_ID INTEGER PRIMARY KEY AUTOINCREMENT, -- AUTOINCREMENT means it will automatically give a new ID
        Food_ID INTEGER NOT NULL,
        Receiver_ID INTEGER NOT NULL,
        Timestamp TEXT NOT NULL, -- Storing as TEXT for simplicity
        Status TEXT NOT NULL,
        FOREIGN KEY (Food_ID) REFERENCES food_listings(Food_ID),
        FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID)
    )
''')

print("--- Tables created or already exist ---")

# --- Part 3: Load Data from CSVs and Put it into Tables ---
# This is like taking your lists from the CSV files and organizing them into the database folders.

csv_files = {
    'food_listings': 'food_listings_data.csv',
    'providers': 'providers_data.csv',
    'receivers': 'receivers_data.csv',
    'claims': 'claims_data.csv'
}

for table_name, csv_file in csv_files.items():
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found. Skipping data loading for {table_name}.")
        continue # Skip to the next file

    try:
        df = pd.read_csv(csv_file, encoding='utf-8')

        # Special handling for date/timestamp columns before saving to SQLite
        if 'Expiry_Date' in df.columns:
            df['Expiry_Date'] = pd.to_datetime(df['Expiry_Date']).dt.strftime('%Y-%m-%d')
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
            # Drop rows where Timestamp became NaT due to errors, if any
            df.dropna(subset=['Timestamp'], inplace=True)


        # Use 'replace' to overwrite existing data every time you run this script.
        # This is good for initial setup. If you run it again, it wipes and reloads.
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"--- Data from '{csv_file}' loaded into '{table_name}' table ---")
    except Exception as e:
        print(f"Error loading data from '{csv_file}' into '{table_name}': {e}")

# --- Part 4: Save all the changes ---
# This is like closing and locking your filing cabinet so nothing gets lost.
conn.commit()

# --- Part 5: Check if Data is There (Optional but good!) ---
# Let's peek into one of the folders to make sure the data is actually inside!
print("\n--- Verifying data in 'food_listings' table (first 5 rows) ---")
df_check = pd.read_sql_query("SELECT * FROM food_listings LIMIT 5;", conn)
print(df_check)

print("\n--- Database setup complete! ---")

# --- Part 6: Close the Connection ---
# Don't forget to close your filing cabinet when you're done!
conn.close()