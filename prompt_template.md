# SYSTEM
You are an expert exhibition hall layout generator. You strictly follow spatial rules, inventory constraints, corridor logic, and geometric validation. You never invent booth sizes, shapes, quantities, entrances, or corridor axes. You always produce a clean, optimized, gap-free, rule-compliant layout as SVG.

# USER
TASK
Generate a complete exhibition hall layout inside an 80 × 40 meter rectangular hall and output it as an SVG file.

DERIVED GLOBAL METRICS (fixed numbers, do not reinterpret)
- Hall area: 3,200 m² (80 m × 40 m).
- Main corridor area: 768 m² (4 m × 40 m vertical + 2 × (4 m × 80 m) horizontals − 2 × (4 m × 4 m) intersections).
- Booth-usable area after corridors: 2,432 m².
- Available inventory area: 2,232 m² across 48 booths (maximum stock, you may use fewer if needed).
- Adjusted inventory figure (area + booth count if fully used): 2,280 (2,232 + 48). Report the actual totals you place.

GLOBAL COORDINATE SYSTEM
- Use a 2D Cartesian coordinate system in meters.
- Origin (0, 0) is at the bottom-left inner corner of the hall.
- Positive X goes left → right, positive Y goes bottom → top.
- The hall boundary is exactly the rectangle from (0, 0) to (80, 40).

HALL GEOMETRY (from the attached plan image)
Use the attached hall plan image as the exact geometry reference. Do NOT change any entrances or the axes of the main corridors. The numeric dimensions below are derived from that image and are mandatory.

1. Hall outline:
- A single rectangle of 80 m (width, left to right) by 40 m (height, bottom to top).

2. Zones (as labeled in the image, with exact coordinates):
- Zone C (top-left strip): x from 0 to 50, y from 35 to 40.
- Zone D (top-right strip): x from 50 to 80, y from 35 to 40.
- Zone A (central-left area): x from 0 to 50, y from 5 to 35.
- Zone B (central-right area): x from 50 to 80, y from 5 to 35.
- Zone E (bottom-left strip): x from 0 to 50, y from 0 to 5.
- Zone F (bottom-right strip): x from 50 to 80, y from 0 to 5.
You must respect these zone boundaries exactly and must not modify them.

CRITICAL ZONE CONSTRAINT:
- Zones C, D, E, and F are 5 meters deep, but the main corridor overlaps them by 2 meters (from the axis).
- This leaves EXACTLY 3 meters of usable depth in these zones.
- Therefore, you can ONLY place booths with a depth of exactly 3 meters in Zones C, D, E, and F.
- Due to the 4:1 aspect ratio limit, the maximum width for a 3m deep booth is 12m.
- CONSEQUENCE: Zones C, D, E, and F can ONLY accept booths of size 36 m² or smaller (e.g., 30, 20, 18, 15, 12 m²).
- DO NOT attempt to place larger booths (40 m² and up) in these zones.

3. Entrance / exit nodes (white dots in the image, fixed coordinates):
There are four entrance/exit nodes located exactly as follows:
- MAIN ENTRANCE (top center): (50, 40), on the top edge of the hall.
- LEFT ENTRANCE: (0, 35), on the left edge at the intersection with the upper main horizontal corridor axis.
- RIGHT ENTRANCE: (80, 35), on the right edge at the intersection with the upper main horizontal corridor axis.
- BOTTOM ENTRANCE: (50, 0), on the bottom edge of the hall.
These four entrance nodes are fixed and must NOT be moved, deleted, or duplicated. The top node is the main entrance and is the most important one.

4. Main corridor axes (red lines in the image, fixed coordinates):
The red lines in the image are the axes of the main corridors. They are fixed and must be used exactly as shown:
- Vertical main corridor axis: the line x = 50, running continuously from y = 0 to y = 40 (connecting bottom entrance, center of the hall, and main entrance).
- Upper horizontal main corridor axis: the line y = 35, running from x = 0 to x = 80 (connecting left and right entrances and intersecting the vertical axis).
- Lower horizontal main corridor axis: the line y = 5, running from x = 0 to x = 80 (intersecting the vertical axis and separating zones E/F from A/B).
You must generate main corridors centered on these axes with the required width. You may NOT invent additional main corridor axes or move these ones.

HARD REQUIREMENTS
1. Allowed booth sizes (inventory counts)
You must place exactly the following booths:
- 2 × 200 m²
- 3 × 100 m²
- 2 × 90 m²
- 3 × 80 m²
- 4 × 60 m²
- 5 × 48 m²
- 4 × 40 m²
- 5 × 30 m²
- 5 × 20 m²
- 5 × 18 m²
- 4 × 15 m²
- 6 × 12 m²

Rules:
- You must only use the booth sizes provided above.
- Do not create additional booth sizes.
- Do not merge booths.
- Do not subdivide booths.

2. Booth geometry constraints
Each booth must:
- be a perfect rectangle,
- be aligned to a 0.25 m grid in the global coordinate system,
- have a minimum side length of at least 3 m,
- have a maximum aspect ratio (longer side / shorter side) of 4:1,
- touch at least one corridor edge (main or secondary or tertiary) for access,
- not overlap other booths or corridors,
- belong to a clean rectangular booth island (no concave or stepped island shapes).
- Corridor access rule: at least one full side of every booth must be flush with a corridor edge; no booth may be completely surrounded by other booths without corridor contact.

3. Corridor rules
Main corridors:
- Must be centered exactly on the fixed axes: x = 50, y = 35, and y = 5.
- Main corridor width = exactly 4 m (2 m offset to each side of the axis line).
- Corridors are strictly orthogonal.
- Must connect all four entrance/exit nodes to each other via the main corridor network.
- You must not move, rotate, delete, or add main corridor axes.

Secondary and tertiary corridors:
- Allowed only in Zones A and B.
- Widths between 2.5 m and 3.5 m (inclusive).
- May be discontinuous, staggered, or zig-zag.
- Must not be dead-ends: every secondary/tertiary corridor must connect to a main corridor or to another corridor loop.
- Must improve circulation, visibility, and subdivision efficiency.
- Must not fragment space unnecessarily.

Zones C, D, E, and F:
- Booth-only zones.
- No secondary or tertiary corridors are allowed inside these zones.

4. Placement priority and scoring
Place booths in this priority order:
1) 200 m²
2) 100, 90, 80 m²
3) 60, 48, 40 m²
4) 30, 20, 18, 15, 12 m²
- After placing the largest booths near entrances/main corridors, introduce secondary/tertiary corridors to expand frontage for the remaining inventory.
- You may use fewer booths than the available inventory if space/frontage runs out; never exceed the provided counts. Report what was placed and what remains unused.

When choosing positions, maximize the following scores:
- Closeness to the main entrance (shorter Euclidean or Manhattan distance is better),
- Frontage along main corridors (longer is better),
- Frontage along any corridor,
- Number of open sides,
- Corner positions,
- Long edges facing corridors,
- Geometric cleanliness of booth islands.

OUTPUT FORMAT
Your final output must contain:
- the 80 × 40 m hall boundary as in the plan image and numeric description,
- all main corridors exactly along the axes x = 50, y = 35, and y = 5 with their 4 m width,
- all secondary and tertiary corridors (only in Zones A and B) with their widths,
- all booth rectangles with precise coordinates in this coordinate system,
- labels inside each booth showing its area (for example: "60 m²"),
- no overlapping geometry,
- no unused gaps or meaningless voids,
- no invented booth sizes.

PROCESS STEPS (you must follow them in order)
1. Read and adopt the hall geometry, entrance nodes, and main corridor axes exactly from the numeric description and the attached plan image.
2. Generate the main corridors centered on the given axes, connecting all entrances.
3. Place the largest booths first (near entrances/main corridors), then add secondary and tertiary corridors in Zones A and B to unlock frontage.
4. Subtract corridor areas from the hall interior.
5. Form rectangular booth islands in the remaining areas.
6. Place as many booths as fit according to the inventory and placement priority (do not exceed counts).
7. Adjust positions to maximize the scoring criteria.
8. Validate inventory and geometry.
9. Ensure the layout is dense, orthogonal, and visually balanced.
10. Produce the final SVG.

MANDATORY SELF-VALIDATION BEFORE OUTPUT
Before outputting the SVG, internally verify that:
- Hall area = 3,200 m² and main corridor area = 768 m²; remaining booth area = 2,432 m².
- Placed inventory does not exceed available counts: max 48 booths, 2,232 m²; report the actual placed totals and the unused stock.
- No additional booth sizes exist.
- No booth violates the minimum side length or maximum aspect ratio.
- Every booth touches at least one corridor edge (main or secondary or tertiary).
- No booth is fully enclosed by other booths without corridor frontage.
- There are no gaps, voids, or leftover unusable pockets.
- All corridor rules and zone rules are respected; secondary/tertiary corridors are not dead-ends and connect to the network.
- All entrances and main corridor axes match the numeric description and the attached plan image.
- The layout fills the hall cleanly and orthogonally.

FINAL ANSWER FORMAT
1. First, output a short textual confirmation that all validation checks have passed.
2. Then output the complete exhibition layout as a valid SVG string. The SVG must contain the hall boundary, corridors, booth rectangles, and text labels with booth areas.
