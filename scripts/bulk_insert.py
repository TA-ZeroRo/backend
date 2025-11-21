"""
Generate bulk insert SQL for all campaigns
"""
import json

# Load processed data
with open(r'c:\Users\goodj\Desktop\TA-ZeroRo\backend\scripts\campaigns_processed.json', 'r', encoding='utf-8') as f:
    campaigns = json.load(f)

# Skip first one (already inserted)
campaigns_to_insert = campaigns[1:]

# Generate VALUES clauses
values_list = []
for c in campaigns_to_insert:
    # Escape single quotes in strings
    def escape_sql(s):
        if s is None:
            return 'NULL'
        return "'" + str(s).replace("'", "''") + "'"

    title = escape_sql(c.get('title'))
    description = escape_sql(c.get('description'))
    host_organizer = escape_sql(c.get('host_organizer'))
    campaign_url = escape_sql(c.get('campaign_url'))
    image_url = escape_sql(c.get('image_url'))
    start_date = escape_sql(c.get('start_date')) if c.get('start_date') else 'NULL'
    end_date = escape_sql(c.get('end_date')) if c.get('end_date') else 'NULL'
    region = escape_sql(c.get('region'))
    category = escape_sql(c.get('category'))
    status = escape_sql(c.get('status'))
    submission_type = escape_sql(c.get('submission_type'))

    values = f"""(
  {title},
  {description},
  {host_organizer},
  {campaign_url},
  {image_url},
  {start_date},
  {end_date},
  {region},
  {category},
  {status},
  {submission_type}
)"""
    values_list.append(values)

# Create INSERT statement
insert_sql = f"""INSERT INTO campaigns (
  title, description, host_organizer, campaign_url, image_url,
  start_date, end_date, region, category, status, submission_type
) VALUES
{','.join(values_list)};
"""

# Save to file
with open(r'c:\Users\goodj\Desktop\TA-ZeroRo\backend\scripts\bulk_insert.sql', 'w', encoding='utf-8') as f:
    f.write(insert_sql)

print(f"✅ Generated bulk insert SQL for {len(campaigns_to_insert)} campaigns")
print(f"📄 Saved to: bulk_insert.sql")
print(f"\nFirst 500 characters:")
print(insert_sql[:500])
