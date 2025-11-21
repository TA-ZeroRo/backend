"""
Insert batch 4 campaigns individually to avoid SQL escaping issues
"""
import json

# Load processed data
with open(r'c:\Users\goodj\Desktop\TA-ZeroRo\backend\scripts\campaigns_processed.json', 'r', encoding='utf-8') as f:
    campaigns = json.load(f)

# Batch 4 is campaigns 30-35 (index 30-35)
batch_4 = campaigns[30:36]

print(f"Batch 4 campaigns to insert: {len(batch_4)}")
print("\nCampaigns:")
for i, c in enumerate(batch_4, 1):
    print(f"{i}. {c['title']}")

# Generate individual INSERT statements
for i, c in enumerate(batch_4, 1):
    def esc(s):
        if s is None:
            return 'NULL'
        # Use dollar-quoted strings for PostgreSQL to avoid escaping issues
        return f"$${s}$$"

    title = esc(c.get('title'))
    desc = esc(c.get('description'))
    host = esc(c.get('host_organizer'))
    url = esc(c.get('campaign_url'))
    img = esc(c.get('image_url'))
    start = esc(c.get('start_date')) if c.get('start_date') else 'NULL'
    end = esc(c.get('end_date')) if c.get('end_date') else 'NULL'
    region = esc(c.get('region'))
    cat = f"'{c.get('category')}'"  # ENUMs need regular quotes
    status = f"'{c.get('status')}'"
    sub_type = f"'{c.get('submission_type')}'"

    sql = f"""INSERT INTO campaigns (title,description,host_organizer,campaign_url,image_url,start_date,end_date,region,category,status,submission_type)
VALUES ({title},{desc},{host},{url},{img},{start},{end},{region},{cat},{status},{sub_type});"""

    # Save to file
    filename = f"batch_4_row_{i}.sql"
    filepath = f"c:\\Users\\goodj\\Desktop\\TA-ZeroRo\\backend\\scripts\\{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(sql)

    print(f"  Generated: {filename}")

print("\n✅ All individual SQL files generated for Batch 4!")
