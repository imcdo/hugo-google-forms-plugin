#! /usr/bin/env python3
import sys 
import re
import requests

def extract_form_data(url):
    # Ensure we are looking at the viewform page
    if "viewform" not in url:
        url = url.split("?")[0] + "/viewform"

    response = requests.get(url)
    if response.status_code != 200:
        print("Error: Could not fetch form.")
        return

    # Look for the FB_PUBLIC_LOAD_DATA_ variable which contains the form structure
    # This is a bit of a "hack" but very reliable for Google Forms
    match = re.search(r'FB_PUBLIC_LOAD_DATA_ = (.*?);', response.text)
    if not match:
        print("Error: Could not find form data in page.")
        return

    import json
    data = json.loads(match.group(1))
    
    # The nested structure of the Google Form JSON object:
    # data[1][1] contains the list of questions
    questions = data[1][1]
    
    print(f"form_id: \"{data[1][0]}\"")
    print("fields:")
    
    for q in questions:
        try:
            label = q[1]
            # Entry ID is usually in the first sub-item of the question data
            entry_id = q[4][0][0]
            # Map Google's internal type IDs to Hugo-friendly types
            # 0: short text, 1: paragraph, 2: multiple choice, 3: dropdown
            g_type = q[3]
            h_type = "text"
            if g_type == 1: h_type = "textarea"
            if g_type in [2, 3]: h_type = "select"
            
            print(f"  - label: \"{label}\"")
            print(f"    id: \"entry.{entry_id}\"")
            print(f"    type: \"{h_type}\"")
            
            if g_type in [2, 3]:
                print("    options:")
                for opt in q[4][0][1]:
                    print(f"      - \"{opt[0]}\"")
        except (IndexError, TypeError):
            continue

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_spec.py <GOOGLE_FORM_URL>")
    else:
        extract_form_data(sys.argv[1])
