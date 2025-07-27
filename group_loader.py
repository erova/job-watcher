import json

def load_all_groups():
    with open("company_groups.json") as f:
        return json.load(f)

def load_company_group(group_name):
    all_groups = load_all_groups()
    return all_groups.get(group_name, [])