import csv
import pymysql

def import_csv_to_mysql(csv_file_path):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='5568',  # <-- your MySQL password
        database='college_predictor',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    cursor = conn.cursor()
    count = 0

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                cursor.execute("""
                    INSERT INTO college_data (
                        institute_name, academic_program, seat_stype,
                        gender_type, opening_rank, closing_rank,
                        state, institute_type
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['Institute'],
                    row['Academic Program Name'],
                    row['Seat Type'],
                    row['Gender'],
                    int(row['Opening Rank']) if row['Opening Rank'].isdigit() else None,
                    int(row['Closing Rank']) if row['Closing Rank'].isdigit() else None,
                    row['State'],
                    row['Institute Type']
                ))
                count += 1
            except Exception as e:
                print(f"⚠️ Error with row: {row}")
                print(f"   → {e}")
                continue

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {count} rows inserted successfully.")

if __name__ == "__main__":
    import_csv_to_mysql('data/josaa_data.csv')
