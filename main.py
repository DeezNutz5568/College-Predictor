import pymysql

# DB config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '5568',  # replace this
    'database': 'college_predictor',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_user_inputs():
    rank = int(input("🎯 Enter your rank: "))
    category = input("🏷️  Enter your category (OPEN, OBC-NCL, EWS, SC, ST, etc.): ").upper().strip()
    gender = input("🚻 Enter your gender (M/F): ").strip().upper()
    home_state = input("🏠 Enter your home state: ").strip().title()
    filter_option = input("🔘 Filter by state? (1: Home State only, 2: Other States only, 3: All): ").strip()
    return rank, category, gender, home_state, filter_option

def fetch_colleges(rank, category, gender, home_state, filter_option):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    gender_clause = "'Gender-Neutral'"
    if gender == "F":
        gender_clause = "'Gender-Neutral', 'Female-only (including Supernumerary)'"

    state_filter = ""
    if filter_option == "1":
        state_filter = "AND state = %s"
    elif filter_option == "2":
        state_filter = "AND state != %s"

    query = f"""
    SELECT * FROM college_data
    WHERE 
        seat_stype = %s
        AND gender_type IN ({gender_clause})
        AND closing_rank >= %s
        {state_filter}
    ORDER BY closing_rank ASC
    LIMIT 100;
    """

    try:
        if filter_option in ["1", "2"]:
            cursor.execute(query, (category, rank, home_state))
        else:
            cursor.execute(query, (category, rank))
        results = cursor.fetchall()
    except Exception as e:
        print("❌ Query error:", e)
        results = []

    conn.close()
    return results

def display_colleges(results):
    if not results:
        print("😢 No matching colleges found.")
        return

    print("\n🎓 Matching Colleges:\n")
    for row in results:
        print(f"{row['institute_name']} | {row['academic_program']}")
        print(f"→ Rank Range: {row['opening_rank']} - {row['closing_rank']}")
        print(f"→ Gender: {row['gender_type']} | Institute Type: {row['institute_type']} | State: {row['state']}")
        print("-" * 60)

# Main
if __name__ == "__main__":
    rank, category, gender, home_state, filter_option = get_user_inputs()
    colleges = fetch_colleges(rank, category, gender, home_state, filter_option)
    display_colleges(colleges)
