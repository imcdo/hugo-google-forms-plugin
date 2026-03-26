#! /usr/bin/env python3
import sys
import re
import requests
import json

def extract_form_data(url):
    # Ensure we are looking at the viewform page
    if "viewform" not in url:
        url = url.split("?")[0] + "/viewform"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching form: {e}")
        return

    # Extract the JS variable containing form metadata
    match = re.search(r'FB_PUBLIC_LOAD_DATA_ = (.*?);', response.text)
    if not match:
        print("Error: Could not find form data. Is the form public?")
        return

    data = json.loads(match.group(1))
    
    # data[1][1] = List of questions
    # data[1][0] = Form ID
    form_id = data[1][0]
    questions = data[1][1]
    
    print(f"form_id: \"{form_id}\"")
    print("submit_text: \"Submit\"")
    print("fields:")
    
    for q in questions:
        try:
            # Question Metadata mapping:
            # q[1] = Label/Title
            # q[3] = Type ID (0: short, 1: long, 2: radio, 3: dropdown, 5: check, 7: scale)
            # q[4][0][0] = Entry ID
            # q[4][0][2] = Required (1 = True, 0 = False)
            
            label = q[1]
            entry_id = q[4][0][0]
            g_type = q[3]
            
            # Detect if field is required
            is_required = True if q[4][0][2] == 1 else False
            
            # Map Google Types to our YAML Schema
            h_type = "text"
            options = []
            rating_range = None

            if g_type == 1:
                h_type = "paragraph"
            elif g_type == 2 or g_type == 3:
                h_type = "radio"
                # Extract options from q[4][0][1]
                options = [opt[0] for opt in q[4][0][1]]
            elif g_type == 7:
                h_type = "rating"
                # Scale min/max is usually in q[4][0][3]
                rating_range = [int(q[4][0][3][0]), int(q[4][0][3][-1])]

            # Print YAML Block
            print(f"  - label: \"{label}\"")
            print(f"    id: \"entry.{entry_id}\"")
            print(f"    type: \"{h_type}\"")
            print(f"    required: {str(is_required).lower()}")
            
            if options:
                print("    options:")
                for opt in options:
                    print(f"      - \"{opt}\"")
            
            if rating_range:
                print(f"    range: [{rating_range[0]}, {rating_range[1]}]")
                
        except (IndexError, TypeError):
            # Skip items that aren't actual questions (like section headers)
            continue

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_spec.py <GOOGLE_FORM_URL>")
    else:
        extract_form_data(sys.argv[1])