"""
Batch insert campaigns to Supabase using MCP
"""
import json

# Load processed data
with open(r'c:\Users\goodj\Desktop\TA-ZeroRo\backend\scripts\campaigns_processed.json', 'r', encoding='utf-8') as f:
    campaigns = json.load(f)

print(f"Total campaigns to insert: {len(campaigns)}")

# Generate INSERT statements in batches of 10
batch_size = 10
for i in range(0, len(campaigns), batch_size):
    batch = campaigns[i:i+batch_size]

    # Generate VALUES for this batch
    values_list = []
    for c in batch:
        def esc(s):
            if s is None:
                return 'NULL'
            return "'" + str(s).replace("'", "''").replace("\\", "\\\\") + "'"

        title = esc(c.get('title'))
        desc = esc(c.get('description'))
        host = esc(c.get('host_organizer'))
        url = esc(c.get('campaign_url'))
        img = esc(c.get('image_url'))
        start = esc(c.get('start_date')) if c.get('start_date') else 'NULL'
        end = esc(c.get('end_date')) if c.get('end_date') else 'NULL'
        region = esc(c.get('region'))
        cat = esc(c.get('category'))
        status = esc(c.get('status'))
        sub_type = esc(c.get('submission_type'))

        values_list.append(f"({title},{desc},{host},{url},{img},{start},{end},{region},{cat},{status},{sub_type})")

    sql = f"""INSERT INTO campaigns (title,description,host_organizer,campaign_url,image_url,start_date,end_date,region,category,status,submission_type) VALUES {','.join(values_list)};"""

    # Save to file
    filename = f"batch_{i//batch_size + 1}.sql"
    with open(f"c:\\Users\\goodj\\Desktop\\TA-ZeroRo\\backend\\scripts\\{filename}", 'w', encoding='utf-8') as f:
        f.write(sql)

    print(f"Batch {i//batch_size + 1}: {len(batch)} campaigns -> {filename}")

print("\n✅ All batch SQL files generated!")
