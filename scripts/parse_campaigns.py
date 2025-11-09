"""
Parse campaign.md markdown table and convert to JSON for Supabase insertion
"""
import re
import json
from datetime import datetime

def parse_markdown_table(filepath):
    """Parse markdown table from campaign.md"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find table rows
    table_rows = [line for line in lines if line.strip().startswith('|') and '---' not in line]

    # Skip first 2 rows (headers)
    data_rows = table_rows[2:]

    campaigns = []
    for row in data_rows:
        # Split by | and clean
        cells = [cell.strip() for cell in row.split('|')]

        # Skip rows with too few cells or empty rows
        if len(cells) < 8:
            continue

        # Check if first non-empty cell is a number (row_id)
        first_cell = next((c for c in cells if c), None)
        if not first_cell or not first_cell.isdigit():
            continue

        # Map to campaign structure
        # Find index of first non-empty cell (row_id)
        non_empty_cells = [c for c in cells if c]

        if len(non_empty_cells) < 8:
            continue

        # | 컬럼명 | id | title | description | host_organizer | campaign_url | image_url | mission | start_date | end_date | region | category | status | updated_at |
        campaign = {
            'row_id': non_empty_cells[0],
            'title': non_empty_cells[1] if len(non_empty_cells) > 1 else '',
            'description': non_empty_cells[2] if len(non_empty_cells) > 2 else '',
            'host_organizer': non_empty_cells[3] if len(non_empty_cells) > 3 else '',
            'campaign_url': non_empty_cells[4] if len(non_empty_cells) > 4 else '',
            'image_url': non_empty_cells[5] if len(non_empty_cells) > 5 else '',
            'mission': non_empty_cells[6] if len(non_empty_cells) > 6 else '',  # Will be extracted separately
            'start_date': non_empty_cells[7] if len(non_empty_cells) > 7 else '',
            'end_date': non_empty_cells[8] if len(non_empty_cells) > 8 else '',
            'region': non_empty_cells[9] if len(non_empty_cells) > 9 else '',
            'category_raw': non_empty_cells[10] if len(non_empty_cells) > 10 else '',
            'status_raw': non_empty_cells[11] if len(non_empty_cells) > 11 else '',
        }

        campaigns.append(campaign)

    return campaigns

def map_category(category_text):
    """Map Korean category text to ENUM values"""
    category_text = category_text.lower()

    # ENUM: RECYCLING, TRANSPORTATION, ENERGY, ZERO_WASTE, CONSERVATION, EDUCATION, OTHER
    if any(keyword in category_text for keyword in ['재활용', '분리수거', '자원순환', '업사이클']):
        return 'RECYCLING'
    elif any(keyword in category_text for keyword in ['교통', '자전거', '대중교통']):
        return 'TRANSPORTATION'
    elif any(keyword in category_text for keyword in ['에너지', '탄소중립', '탄소', '절전', '미세먼지']):
        return 'ENERGY'
    elif any(keyword in category_text for keyword in ['제로웨이스트', '일회용', '플라스틱', '텀블러']):
        return 'ZERO_WASTE'
    elif any(keyword in category_text for keyword in ['플로깅', '정화', '해양', '해변', '바다', '하천', '환경', '생태', '자연', '보호', '보전']):
        return 'CONSERVATION'
    elif any(keyword in category_text for keyword in ['교육', '체험', '학습']):
        return 'EDUCATION'
    else:
        return 'OTHER'

def map_status(status_text):
    """Map Korean status text to ENUM values"""
    status_text = status_text.lower()

    # ENUM: EXPECT, ACTIVE, EXPIRED
    if any(keyword in status_text for keyword in ['예정', '모집중', '접수중']):
        return 'EXPECT'
    elif any(keyword in status_text for keyword in ['진행', '진행중', '상시']):
        return 'ACTIVE'
    elif any(keyword in status_text for keyword in ['종료', '마감', '완료']):
        return 'EXPIRED'
    else:
        return 'ACTIVE'  # default

def parse_date(date_str):
    """Parse date string to YYYY-MM-DD format"""
    if not date_str or date_str.strip() == '':
        return None

    # Try to extract date in YYYY-MM-DD format
    match = re.search(r'(\d{4})[-.년\s]*(\d{1,2})[-.월\s]*(\d{1,2})', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"

    return None

def extract_missions(mission_text):
    """Extract mission list from mission text"""
    if not mission_text or mission_text.strip() == '':
        return []

    # Split by numbered list (1. 2. 3. or **1. **2. etc)
    missions = re.split(r'\*?\*?\d+\.\s+\*?\*?', mission_text)
    missions = [m.strip() for m in missions if m.strip()]

    return missions

def process_campaigns(filepath):
    """Main processing function"""
    campaigns = parse_markdown_table(filepath)

    processed = []
    mission_templates = []

    for camp in campaigns:
        # Skip if no title
        if not camp['title']:
            continue

        # Process dates
        start_date = parse_date(camp['start_date'])
        end_date = parse_date(camp['end_date'])

        # Map category and status
        category = map_category(camp['category_raw'] + ' ' + camp['description'])
        status = map_status(camp['status_raw'])

        processed_campaign = {
            'title': camp['title'],
            'description': camp['description'] if camp['description'] else None,
            'host_organizer': camp['host_organizer'] if camp['host_organizer'] else None,
            'campaign_url': camp['campaign_url'] if camp['campaign_url'] else None,
            'image_url': camp['image_url'] if camp['image_url'] else None,
            'start_date': start_date,
            'end_date': end_date,
            'region': camp['region'] if camp['region'] else None,
            'category': category,
            'status': status,
            'submission_type': 'MANUAL_GUIDE',  # default
        }

        processed.append(processed_campaign)

        # Extract missions for mission_templates
        missions = extract_missions(camp['mission'])
        for idx, mission_desc in enumerate(missions):
            mission_templates.append({
                'campaign_row_id': camp['row_id'],
                'campaign_title': camp['title'],
                'order': idx + 1,
                'title': f"미션 {idx + 1}",
                'description': mission_desc,
                'verification_type': 'IMAGE',  # default
                'reward_points': 10,  # default
            })

    return processed, mission_templates

if __name__ == '__main__':
    filepath = r'c:\Users\goodj\Desktop\TA-ZeroRo\backend\docs\campaign.md'

    campaigns, missions = process_campaigns(filepath)

    # Save to JSON
    with open(r'c:\Users\goodj\Desktop\TA-ZeroRo\backend\scripts\campaigns_processed.json', 'w', encoding='utf-8') as f:
        json.dump(campaigns, f, ensure_ascii=False, indent=2)

    with open(r'c:\Users\goodj\Desktop\TA-ZeroRo\backend\scripts\missions_processed.json', 'w', encoding='utf-8') as f:
        json.dump(missions, f, ensure_ascii=False, indent=2)

    print(f"✅ Processed {len(campaigns)} campaigns")
    print(f"✅ Processed {len(missions)} missions")

    if len(campaigns) > 0:
        print(f"\nFirst campaign:")
        print(json.dumps(campaigns[0], ensure_ascii=False, indent=2))
    else:
        print("\n⚠️ No campaigns processed")
