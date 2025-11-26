import xml.etree.ElementTree as ET
import sys
import math

def parse_svg_rects(svg_file):
    try:
        tree = ET.parse(svg_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing SVG: {e}")
        return []

    # Namespace handling might be needed depending on SVG generator
    # For now, we search for all 'rect' tags
    rects = []
    # Strip namespace for easier searching
    for elem in root.iter():
        if 'rect' in elem.tag:
            try:
                x = float(elem.attrib.get('x', 0))
                y = float(elem.attrib.get('y', 0))
                w = float(elem.attrib.get('width', 0))
                h = float(elem.attrib.get('height', 0))
                
                # Filter out the main hall boundary (80x40)
                if abs(w - 80) < 0.1 and abs(h - 40) < 0.1:
                    continue
                
                # Filter out corridors (heuristic: very long or specific width)
                # Main corridors are 4m wide.
                if (abs(w - 4) < 0.1 and h > 10) or (abs(h - 4) < 0.1 and w > 10):
                    continue
                    
                rects.append({'x': x, 'y': y, 'w': w, 'h': h, 'area': w * h})
            except ValueError:
                continue
    return rects

def validate_plan(svg_file='plan.svg'):
    print(f"Validating {svg_file}...")
    
    if not os.path.exists(svg_file):
        print(f"Error: {svg_file} does not exist.")
        return False

    booths = parse_svg_rects(svg_file)
    print(f"Found {len(booths)} potential booth rectangles.")

    # Inventory to check against
    required_inventory = {
        200: 1, 100: 2, 90: 2, 80: 2, 60: 4, 48: 4, 40: 4,
        30: 5, 20: 5, 18: 5, 15: 4, 12: 6
    }
    
    found_inventory = {}
    
    errors = []

    for b in booths:
        area = round(b['area'])
        
        # Check aspect ratio
        longer = max(b['w'], b['h'])
        shorter = min(b['w'], b['h'])
        if shorter < 3.0 - 0.01: # Tolerance
             errors.append(f"Booth at ({b['x']}, {b['y']}) has side {shorter} < 3m")
        
        if shorter > 0 and (longer / shorter) > 4.01:
             errors.append(f"Booth at ({b['x']}, {b['y']}) violates aspect ratio 4:1")

        # Count inventory
        found_inventory[area] = found_inventory.get(area, 0) + 1

        # Check Zone C, D, E, F constraint (3m depth)
        # Zone C: x 0-50, y 35-40. Usable y: 37-40 (since corridor is at y=35, width 4 -> y=33 to 37)
        # Wait, corridor is centered at y=35, width 4 => y=33 to y=37.
        # So Zone C (y 35-40) is overlapped by corridor from 35 to 37.
        # Usable Zone C is y=37 to y=40. Depth = 3m.
        
        # Check if booth is in Zone C/D (Top)
        if b['y'] >= 37:
            if b['h'] > 3.01:
                errors.append(f"Booth at ({b['x']}, {b['y']}) in Top Zone has height {b['h']} > 3m")
        
        # Check if booth is in Zone E/F (Bottom)
        # Corridor at y=5, width 4 => y=3 to y=7.
        # Zone E/F is y 0-5.
        # Overlap is y=3 to y=5.
        # Usable Zone E/F is y=0 to y=3. Depth = 3m.
        if b['y'] + b['h'] <= 3:
             if b['h'] > 3.01:
                errors.append(f"Booth at ({b['x']}, {b['y']}) in Bottom Zone has height {b['h']} > 3m")

    # Verify Inventory
    print("\nInventory Check:")
    for size, count in required_inventory.items():
        found = found_inventory.get(size, 0)
        status = "OK" if found == count else f"MISMATCH (Found {found})"
        print(f"Size {size}: Expected {count} -> {status}")
        if found != count:
            errors.append(f"Inventory mismatch for size {size}: Expected {count}, Found {found}")

    if errors:
        print("\nValidation FAILED with errors:")
        for e in errors:
            print(f"- {e}")
        return False
    else:
        print("\nValidation PASSED!")
        return True

import os
if __name__ == "__main__":
    validate_plan()
