import sqlite3
import os
# Database file name
DB_FILE = "sqlite-latest.sqlite"
OUTPUT_FILE = "t2_ships.txt"

def get_t2_ships():
    """Retrieves all type_ids and names of Tech 2 ships from the SDE."""
    query = """
    SELECT typeID, typeName 
    FROM invTypes 
    WHERE groupID IN (
        SELECT groupID FROM invGroups WHERE categoryID = 6
    )
    AND typeID IN (
        SELECT typeID FROM invMetaTypes WHERE metaGroupID = 2
    );
    """
    
    if not os.path.exists(DB_FILE):
        print("SDE database not found! Please ensure the SDE is downloaded and extracted.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query)
    ships = cursor.fetchall()
    conn.close()
    
    return ships

def save_t2_ships():
    """Fetches and saves the T2 ships to a file."""
    ships = get_t2_ships()
    if not ships:
        print("No T2 ships found or SDE not available.")
        return
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for type_id, name in ships:
            f.write(f"{type_id}, {name}\n")
    
    print(f"Saved {len(ships)} T2 ships to {OUTPUT_FILE}.")

def main():
    save_t2_ships()

if __name__ == "__main__":
    main()

