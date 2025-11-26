import json
import re

def build_prompt():
    with open('prompt_template.md', 'r') as f:
        content = f.read()

    # Split content by headers
    # We expect # SYSTEM and # USER headers
    
    system_match = re.search(r'# SYSTEM\n(.*?)(?=\n# USER|\Z)', content, re.DOTALL)
    user_match = re.search(r'# USER\n(.*)', content, re.DOTALL)

    if not system_match or not user_match:
        print("Error: Could not find # SYSTEM or # USER sections in prompt_template.md")
        return

    system_content = system_match.group(1).strip()
    user_content = user_match.group(1).strip()

    prompt_data = {
        "messages": [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]
    }

    with open('prompt.json', 'w') as f:
        json.dump(prompt_data, f, indent=4)
    
    print("Successfully rebuilt prompt.json")

if __name__ == "__main__":
    build_prompt()
