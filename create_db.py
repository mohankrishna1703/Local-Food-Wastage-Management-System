# These lines bring in tools we need
import pandas as pd # Tool to read CSV files easily
import sqlite3 # Tool to work with our database

# --- Step 1: Connect to our database ---
# This line tells Python to create a database file called 'food_wastage.db'
# If the file already exists, it will connect to it.
conn = sqlite3.connect('food_wastage.db')
cursor = conn.cursor() # A 'cursor' is like a remote control for your database

print("Database 'food_wastage.db' connected successfully!")

# --- Step 2: Create the 'providers' table ---
# This is like creating a shelf in our database fridge for providers.
# We define what kind of information (columns) each provider will have.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS providers (
        Provider_ID INTEGER PRIMARY KEY, -- A unique number for each provider
        Name TEXT,         -- The name of the provider (like "Restaurant ABC")
        Type TEXT,         -- What kind of provider (like "Restaurant", "Grocery Store")
        Address TEXT,      -- Their street address
        City TEXT,         -- The city they are in
        Contact TEXT       -- Their phone number or email
    )
''')
conn.commit() # Save the changes to the database

print("Table 'providers' created.")

# --- Step 3: Load data from 'providers_data.csv' into the 'providers' table ---
try:
    # Using cp1252 encoding as a common fallback for Windows
    providers_df = pd.read_csv('providers_data.csv', encoding='cp1252')
    providers_df.to_sql('providers', conn, if_exists='replace', index=False)
    conn.commit() # Save the changes
    print("Data from 'providers_data.csv' loaded into 'providers' table.")
except FileNotFoundError:
    print("Error: providers_data.csv not found. Make sure it's in the same folder as this script.")
except Exception as e: # Catch other potential errors during reading/loading
    print(f"Error loading providers_data.csv: {e}")


# --- Repeat for 'receivers' table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS receivers (
        Receiver_ID INTEGER PRIMARY KEY,
        Name TEXT,
        Type TEXT,
        City TEXT,
        Contact TEXT
    )
''')
conn.commit()
print("Table 'receivers' created.")
try:
    # Using cp1252 encoding as a common fallback for Windows
    receivers_df = pd.read_csv('receivers_data.csv', encoding='cp1252')
    receivers_df.to_sql('receivers', conn, if_exists='replace', index=False)
    conn.commit()
    print("Data from 'receivers_data.csv' loaded into 'receivers' table.")
except FileNotFoundError:
    print("Error: receivers_data.csv not found. Make sure it's in the same folder as this script.")
except Exception as e:
    print(f"Error loading receivers_data.csv: {e}")


# --- Repeat for 'food_listings' table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID INTEGER PRIMARY KEY,
        Food_Name TEXT,
        Quantity INTEGER,
        Expiry_Date TEXT, -- We'll store dates as text for simplicity
        Provider_ID INTEGER,
        Provider_Type TEXT,
        Location TEXT,
        Food_Type TEXT,
        Meal_Type TEXT
    )
''')
conn.commit()
print("Table 'food_listings' created.")
try:
    # Using cp1252 encoding as a common fallback for Windows
    food_listings_df = pd.read_csv('food_listings_data.csv', encoding='cp1252')

    # --- NEW: Clean 'Food_ID' to ensure it's a number ---
    # Convert 'Food_ID' to numeric, replacing any non-numeric values with NaN (Not a Number)
    food_listings_df['Food_ID'] = pd.to_numeric(food_listings_df['Food_ID'], errors='coerce')
    
    # Drop rows where 'Food_ID' became NaN (meaning it contained non-numeric/problematic data)
    # This ensures only valid integer IDs are inserted.
    food_listings_df.dropna(subset=['Food_ID'], inplace=True)
    
    # Finally, convert 'Food_ID' to integer type
    food_listings_df['Food_ID'] = food_listings_df['Food_ID'].astype(int)
    # --- END NEW CLEANING ---
    
    food_listings_df.to_sql('food_listings', conn, if_exists='replace', index=False)
    conn.commit()
    print("Data from 'food_listings_data.csv' loaded into 'food_listings' table.")
except FileNotFoundError:
    print("Error: food_listings_data.csv not found. Make sure it's in the same folder as this script.")
except Exception as e:
    print(f"Error loading food_listings_data.csv: {e}")


# --- Repeat for 'claims' table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS claims (
        Claim_ID INTEGER PRIMARY KEY,
        Food_ID INTEGER,
        Receiver_ID INTEGER,
        Status TEXT, -- Like 'Pending', 'Completed', 'Cancelled'
        Timestamp TEXT -- We'll store dates/times as text for simplicity
    )
''')
conn.commit()
print("Table 'claims' created.")
try:
    # Using cp1252 encoding as a common fallback for Windows
    claims_df = pd.read_csv('claims_data.csv', encoding='cp1252')
    claims_df.to_sql('claims', conn, if_exists='replace', index=False)
    conn.commit()
    print("Data from 'claims_data.csv' loaded into 'claims' table.")
except FileNotFoundError:
    print("Error: claims_data.csv not found. Make sure it's in the same folder as this script.")
except Exception as e:
    print(f"Error loading claims_data.csv: {e}")


# --- Step 4: Close the database connection ---
conn.close()
print("Database connection closed. All tables created and data loaded!")