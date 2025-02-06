import sqlite3

# Path to your SQLite SDE file
sde_path = "sqlite-latest.sqlite"
conn = sqlite3.connect(sde_path)
cursor = conn.cursor()

# Query to find T2 ship type IDs
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
cursor.execute(query)
t2_ships = cursor.fetchall()

"""# Print T2 ships
for ship in t2_ships:
    print(f"Type ID: {ship[0]}, Name: {ship[1]}")
"""
def get_blueprint_details(type_id):
    """
    Fetch blueprint details for a specific type ID.

    :param type_id: The type ID of the ship.
    :return: A dictionary containing materials and build time.
    """
    # Get blueprint ID
    cursor.execute("SELECT typeID FROM industryActivityProducts WHERE productTypeID = ?", (type_id,))
    blueprint_id = cursor.fetchone()
    if not blueprint_id:
        return None

    blueprint_id = blueprint_id[0]

    # Get materials
    cursor.execute("""
        SELECT materialTypeID, quantity
        FROM industryActivityMaterials
        WHERE typeID = ? AND activityID = 1  -- activityID 1 = manufacturing
    """, (blueprint_id,))
    materials = cursor.fetchall()

    return {
        "blueprint_id": blueprint_id,
        "materials": materials,
    }

t2_ships_blueprints = []
ship_list = []
with open("t2_ships.txt", "r", encoding="utf-8") as f:
    t2_ships = f.readlines()
for line in t2_ships:
    type_id, name = line.strip().split(", ")
    ship_list.append(type_id)
for item in ship_list:
    blueprint_details = get_blueprint_details(item)
    t2_ships_blueprints.append(blueprint_details)


unique_material_ids = set()
# Aggregate unique material IDs
for ship in t2_ships_blueprints:
    for material in ship['materials']:
        material_id = material[0]  # material[0] is the materialTypeID
        unique_material_ids.add(material_id)

# Convert the set to a list (if needed)
unique_material_ids = list(unique_material_ids)

with open("t2_materials.txt", "w", encoding="utf-8") as f:
    for type_id in unique_material_ids:
        f.write(f"{type_id},\n")

print(f"Saved {len(unique_material_ids)} materials to t2_materials.txt.")
