"""
Parse campaign.md markdown table (multiline) and convert to JSON for Supabase insertion
"""
import re
import json
from datetime import datetime

def parse_multiline_markdown_table(filepath):
    """Parse multiline markdown table from campaign.md"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by rows that start with | followed by a digit (campaign row indicator)
    # Pattern: | <digit> | <empty or something> | title...
    campaign_pattern = r'\| (\d+) \|[^\|]*\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|(.*?)\| (\d{4}-\d{2}-\d{2}) \| (\d{4}-\d{2}-\d{2}[^\|]*) \|([^\|]+)\|([^\|]+)\|([^\|]+)\|'

    campaigns = []
    matches = re.finditer(campaign_pattern, content, re.DOTALL)

    for match in matches:
        row_id = match.group(1).strip()
        title = match.group(2).strip()
        description = match.group(3).strip()
        host_organizer = match.group(4).strip()
        campaign_url = match.group(5).strip()
        image_url = match.group(6).strip()
        mission = match.group(7).strip()
        start_date = match.group(8).strip()
        end_date = match.group(9).strip()
        region = match.group(10).strip()
        category_raw = match.group(11).strip()
        status_raw = match.group(12).strip()

        campaign = {
            'row_id': row_id,
            'title': title,
            'description': description,
            'host_organizer': host_organizer,
            'campaign_url': campaign_url,
            'image_url': image_url,
            'mission': mission,
            'start_date': start_date,
            'end_date': end_date,
            'region': region,
            'category_raw': category_raw,
            'status_raw': status_raw,
        }

        campaigns.append(campaign)

    return campaigns

def map_category(category_text, description=''):
    """Map Korean category text to ENUM values"""
    text = (category_text + ' ' + description).lower()

    # ENUM: RECYCLING, TRANSPORTATION, ENERGY, ZERO_WASTE, CONSERVATION, EDUCATION, OTHER
    if any(keyword in text for keyword in ['재활용', '분리수거', '자원순환', '업사이클', 'em비누']):
        return 'RECYCLING'
    elif any(keyword in text for keyword in ['교통', '자전거', '대중교통']):
        return 'TRANSPORTATION'
    elif any(keyword in text for keyword in ['에너지', '탄소중립', '탄소', '절전', '미세먼지', '탄소제로']):
        return 'ENERGY'
    elif any(keyword in text for keyword in ['제로웨이스트', '일회용', '플라스틱', '텀블러', '다회용']):
        return 'ZERO_WASTE'
    elif any(keyword in text for keyword in ['플로깅', '정화', '해양', '해변', '바다', '하천', '환경', '생태', '자연', '보호', '보전', '산림', '나무심기', '돌고래']):
        return 'CONSERVATION'
    elif any(keyword in text for keyword in ['교육', '체험', '학습', '프로그램']):
        return 'EDUCATION'
    else:
        return 'OTHER'

def map_status(status_text):
    """Map Korean status text to ENUM values"""
    text = status_text.lower()

    # ENUM: EXPECT, ACTIVE, EXPIRED
    if any(keyword in text for keyword in ['예정', '모집중', '접수중', 'd-']):
        return 'EXPECT'
    elif any(keyword in text for keyword in ['진행', '진행중', '상시']):
        return 'ACTIVE'
    elif any(keyword in text for keyword in ['종료', '마감', '완료']):
        return 'EXPIRED'
    else:
        return 'ACTIVE'  # default

def parse_date(date_str):
    """Parse date string to YYYY-MM-DD format"""
    if not date_str or date_str.strip() == '':
        return None

    # Extract first YYYY-MM-DD pattern
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if match:
        return match.group(0)

    return None

def extract_missions(mission_text):
    """Extract mission list from mission text"""
    if not mission_text or mission_text.strip() == '':
        return []

    # Split by numbered list (1. 2. 3. or **1. **2. etc)
    missions = re.split(r'\n?\*?\*?\d+\.\s+\*?\*?', mission_text)
    missions = [m.strip() for m in missions if m.strip() and len(m.strip()) > 10]

    return missions

def process_campaigns(filepath):
    """Main processing function"""
    campaigns = parse_multiline_markdown_table(filepath)

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
        category = map_category(camp['category_raw'], camp['description'])
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
        print(f"\n📋 First campaign:")
        print(json.dumps(campaigns[0], ensure_ascii=False, indent=2))
        print(f"\n📋 First 3 missions:")
        for m in missions[:3]:
            print(f"  - {m['campaign_title']}: {m['title']} - {m['description'][:60]}...")
    else:
        print("\n⚠️ No campaigns processed")
