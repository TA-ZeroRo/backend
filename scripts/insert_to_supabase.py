"""
Insert processed campaigns and missions to Supabase using MCP
This script will be called by the user through Claude Code MCP integration
"""
import json

# Load processed data
with open(r'c:\Users\goodj\Desktop\TA-ZeroRo\backend\scripts\campaigns_processed.json', 'r', encoding='utf-8') as f:
    campaigns = json.load(f)

with open(r'c:\Users\goodj\Desktop\TA-ZeroRo\backend\scripts\missions_processed.json', 'r', encoding='utf-8') as f:
    missions = json.load(f)

print(f"📦 Loaded {len(campaigns)} campaigns and {len(missions)} missions")

# Print first campaign as SQL for reference
print("\n📋 Sample SQL INSERT for first campaign:")
c = campaigns[0]
print(f"""
INSERT INTO campaigns (
  title, description, host_organizer, campaign_url, image_url,
  start_date, end_date, region, category, status, submission_type
) VALUES (
  '{c['title']}',
  '{c['description'][:50]}...',
  '{c['host_organizer']}',
  '{c['campaign_url']}',
  '{c['image_url']}',
  '{c['start_date']}',
  '{c['end_date']}',
  '{c['region']}',
  '{c['category']}',
  '{c['status']}',
  '{c['submission_type']}'
);
""")

# Create batch insert statements
print("\n" + "="*80)
print("Ready to insert via Supabase MCP")
print("="*80)
