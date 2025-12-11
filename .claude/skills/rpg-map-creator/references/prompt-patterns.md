# Prompt Patterns for z-image turbo

Proven prompt patterns and best practices for generating RPG maps with z-image turbo model in ComfyUI.

## Table of Contents

- General Principles
- Core Prompt Structure
- Map Type Templates
- Quality Boosters
- Style Modifiers
- Common Pitfalls
- Advanced Techniques

## General Principles

### Prompt Structure Hierarchy
1. **Map type and perspective** (most important - establishes context)
2. **Specific elements** (what's in the map)
3. **Style descriptors** (how it should look)
4. **Atmosphere/mood** (feeling and lighting)
5. **Quality tags** (technical quality)

### Key Rules for z-image turbo
- **Be specific**: "stone castle with four towers" > "castle"
- **Front-load important details**: Put critical elements first
- **Use consistent terminology**: Pick terms and stick with them
- **Separate concepts with commas**: Clear parsing
- **Avoid contradictions**: Don't ask for incompatible elements
- **Include perspective**: Always specify "top-down view" for maps
- **Mention grid if needed**: "square grid overlay" or "hex grid"

### Effective Descriptor Types
- **Material descriptors**: stone, wood, metal, crystal
- **Condition descriptors**: ancient, ruined, pristine, weathered
- **Scale descriptors**: massive, small, sprawling, cramped
- **Atmospheric descriptors**: foggy, bright, ominous, peaceful
- **Color descriptors**: warm tones, cool colors, monochromatic
- **Style descriptors**: hand-drawn, satellite view, game map, isometric

## Core Prompt Structure

### Basic Template
```
[MAP TYPE], [PERSPECTIVE], [KEY ELEMENTS], [TERRAIN FEATURES], [STYLE], [ATMOSPHERE], [COLOR SCHEME], [QUALITY TAGS]
```

### Example Application
```
Fantasy world map, top-down view, three continents separated by ocean, mountain ranges, forests, rivers, hand-drawn on aged parchment, warm earth tones, detailed cartography, high quality
```

### Template for Each Map Type

**World Map:**
```
[Theme] world map, top-down view, showing [continents/regions], [major features: mountains/rivers/forests], [political boundaries if any], [style: parchment/satellite/etc], [color scheme], [decorative elements: compass rose/border], detailed cartography
```

**Regional Map:**
```
[Theme] regional map, [perspective], [central location], surrounded by [terrain], [settlements/points of interest], [roads/paths], [style], [color scheme], clear and detailed
```

**Battle Map:**
```
Battle map, top-down view, [dimensions], [grid type], [setting/environment], [terrain features], [cover elements], [hazards], [style], high contrast, optimized for gameplay
```

**Dungeon Map:**
```
Dungeon map, top-down view, [structure type], [room layout], [key features], [doors/connections], [grid if needed], [wall/floor style], [lighting atmosphere], detailed and clear
```

## Map Type Templates

### World/Continent Maps

**Fantasy World - Parchment Style:**
```
Fantasy world map on aged parchment, top-down view, [describe continents and major land masses], mountain ranges shown as small peaks, forests as tree symbols, major rivers in blue, [kingdoms/regions with boundaries], compass rose in corner, decorative border, warm sepia tones, hand-drawn cartography style, detailed but readable
```

**Sci-Fi Star System:**
```
Science fiction star system map, top-down schematic view, central star, [number] orbiting planets, asteroid belt, [space stations/outposts], trade routes shown as glowing lines, color-coded territorial zones, holographic display aesthetic, deep space background, clean technical design
```

**Post-Apocalyptic Continent:**
```
Post-apocalyptic continent map, top-down view, [continent shape], radiation zones in red, dead cities marked, survivor settlements as small fortified dots, pre-war highway system faded, wasteland terrain, torn and weathered paper style, faded colors, danger zone markings
```

### Regional/Local Area Maps

**Fantasy Village Region:**
```
Fantasy regional map, top-down view, fortified village in center, surrounding farmland with fields, [terrain features: forest/river/hills], dirt roads connecting outlying buildings, [specific landmarks], hand-drawn on parchment, warm colors, clear details, adventure map style
```

**Cyberpunk City District:**
```
Cyberpunk district map, top-down view, several city blocks, main street with neon establishments, narrow alleys, [key buildings], elevated highway crossing, underground access points marked, dark background with neon color highlights, tactical map style, grid layout
```

**Wilderness Exploration:**
```
Wilderness region map, top-down view, [primary terrain type], [natural features], [any structures or ruins], [rivers/water], trails and paths, unexplored areas, illustrated map style, natural color palette, sense of adventure
```

### Battle/Encounter Maps

**Forest Encounter:**
```
Fantasy battle map, top-down view, 40x40 feet, square grid with 5-foot squares, forest clearing, [number] large trees providing full cover, fallen log for partial cover, small stream diagonally across map, scattered rocks, grass and dirt ground, natural lighting, high contrast, clear grid lines, optimized for virtual tabletop, detailed textures
```

**Dungeon Room Combat:**
```
Dungeon battle map, top-down view, 30x30 feet, square grid, stone chamber, [pillars/obstacles], [elevation changes if any], stone floor with detail, walls clearly defined, [doors/exits], torch-lit atmosphere, shadows but clear visibility, tactical clarity, high resolution
```

**Urban Street Fight:**
```
Modern urban battle map, top-down view, 50x50 feet, square grid, city street, parked vehicles for cover, building corners, [specific elements like mailbox/bench], sidewalks clearly defined, asphalt road texture, street markings, contemporary setting, clear tactical positions
```

**Spaceship Interior Combat:**
```
Sci-fi battle map, top-down view, 35x40 feet, square grid, spaceship corridor, [rooms/areas], consoles and equipment for cover, doorways, metallic floor with panels, walls with detail, sci-fi lighting, clean but tactical, high-tech aesthetic
```

### Dungeon/Interior Maps

**Classic Dungeon:**
```
Fantasy dungeon map, top-down view, [describe layout: corridors and rooms], stone walls [thick/thin], [room purposes and features], doors marked, [secret doors if any], stone floor, grid overlay, classic dungeon aesthetic, clear and readable, old-school RPG style
```

**Haunted Mansion Floor:**
```
Gothic mansion interior map, top-down view, [floor layout], [room names and purposes], Victorian furniture indicated, [specific features: fireplaces/staircases], wooden floors, wallpapered walls, elegant but eerie, detailed floor plan, dark wood tones
```

**Sci-Fi Facility:**
```
Science fiction facility map, top-down view, [layout description], metallic walls, [rooms and purposes], doors and airlocks, computer terminals, [specific features], grid floor pattern, clean technical aesthetic, futuristic design, clear labeling
```

## Quality Boosters

### Technical Quality Tags
Add these to the end of prompts to improve output:
- `high quality`
- `detailed`
- `high resolution`
- `professional`
- `clear and readable`
- `sharp details`
- `well-composed`

### Style Quality Tags
- `detailed cartography`
- `professional map design`
- `game-ready`
- `publication quality`
- `master cartographer style`
- `AAA game asset quality`

### Map-Specific Quality Tags
- For battle maps: `optimized for virtual tabletop`, `tactical clarity`, `high contrast`
- For world maps: `detailed cartography`, `professional atlas quality`
- For dungeon maps: `clear layout`, `gameplay-optimized`, `easy to read`

## Style Modifiers

### Artistic Styles
- `hand-drawn style` - Traditional map aesthetic
- `watercolor` - Soft, artistic feel
- `ink illustration` - Bold lines, traditional
- `digital art` - Clean, modern
- `painterly` - Art-focused, less geometric
- `pixel art` - Retro game style
- `engraving style` - Classical, detailed lines
- `woodcut style` - Bold, medieval feel

### Map Styles
- `parchment style` - Classic fantasy map
- `satellite view` - Modern, realistic
- `tactical map` - Clean, game-focused
- `illustrated map` - Story-book quality
- `schematic diagram` - Technical, precise
- `antique map style` - Historical aesthetic
- `game board style` - Clear, functional
- `atlas page` - Professional cartography

### Era/Setting Styles
- `medieval cartography`
- `Age of Exploration map style`
- `modern topographic map`
- `military tactical map`
- `fantasy game map`
- `sci-fi holographic display`
- `ancient scroll`

## Atmosphere/Mood Descriptors

### Lighting Atmospheres
- `bright daylight`
- `golden hour lighting`
- `overcast and moody`
- `torch-lit` (dungeons)
- `neon-lit` (cyberpunk)
- `dramatic lighting`
- `atmospheric fog`
- `clear visibility`

### Mood Descriptors
- `ominous atmosphere`
- `welcoming and safe`
- `mysterious and ancient`
- `dangerous and foreboding`
- `peaceful and serene`
- `war-torn and desperate`
- `magical and wondrous`
- `desolate and abandoned`

## Color Schemes

### Preset Palettes
- `warm earth tones` - Browns, tans, warm greens
- `cool color palette` - Blues, greens, purples
- `monochromatic` - Single color variations
- `high contrast` - Strong color differences
- `desaturated` - Muted, realistic
- `vibrant colors` - Saturated, fantasy
- `sepia toned` - Classic aged map
- `full color` - Natural color range

### Theme-Appropriate Colors
- Fantasy: `warm earth tones, rich jewel colors, magical glows`
- Sci-Fi: `cool blues and silvers, neon accents, metallic tones`
- Horror: `desaturated, dark greys, blood red accents`
- Post-Apoc: `dusty browns, rust colors, faded tones`
- Cyberpunk: `neon pink and blue, dark background, high contrast`

## Common Pitfalls and Solutions

### Problem: Map lacks perspective clarity
**Solution:** Always include explicit perspective
- ❌ "Forest map with trees and river"
- ✅ "Forest map, top-down view, with trees and river"

### Problem: Elements are unclear or ambiguous
**Solution:** Be specific about materials and types
- ❌ "Castle on map"
- ✅ "Stone castle with four corner towers, curtain walls, central keep"

### Problem: Style is inconsistent
**Solution:** Commit to one style and reinforce it
- ❌ "Parchment map, satellite view, photorealistic"
- ✅ "Hand-drawn parchment map, stylized illustration, cartography aesthetic"

### Problem: Too cluttered or too empty
**Solution:** Balance detail description
- ❌ "Map with stuff"
- ❌ "Map with ancient stone castle fortress with detailed crenellations and iron-banded oak doors and a moat with drawbridge and four corner towers with conical roofs and arrow slits and..." (too much)
- ✅ "Medieval castle with towers, walls, and moat"

### Problem: Grid is unclear or overwhelming
**Solution:** Specify grid style clearly
- ❌ "With grid"
- ✅ "Square grid overlay, subtle but visible, 5-foot squares"

### Problem: Wrong scale for map type
**Solution:** Match detail to map scale
- ❌ "World map showing individual trees"
- ✅ "World map with forests shown as green regions"

### Problem: Colors are muddy or unclear
**Solution:** Specify color scheme and contrast
- ❌ "Colorful map"
- ✅ "High contrast color scheme, distinct terrain colors, clear boundaries"

## Advanced Techniques

### Layering Descriptors
Build prompts in layers of specificity:
```
[Base] Battle map, top-down view, 40x40 feet
[Structure] Stone dungeon chamber with pillars
[Details] Broken furniture, debris, two doorways
[Atmosphere] Torch-lit, atmospheric shadows
[Style] Fantasy game asset, detailed textures
[Technical] Square grid, high contrast, VTT-optimized
```

### Emphasis Through Position
Put most important elements first:
- "Top-down fantasy battle map with trees" (emphasizes it's a map)
- "Trees in a battle map setting, top-down" (emphasizes trees)

### Style Mixing (Use Carefully)
Can combine compatible styles:
- ✅ "Hand-drawn parchment map with watercolor terrain"
- ✅ "Isometric view with pixel art style"
- ❌ "Photorealistic cartoon style" (contradictory)

### Negative Space Description
Describe what's NOT there:
- "Sparse battlefield, mostly open ground with few obstacles"
- "Minimalist dungeon, clean corridors, no clutter"

### Comparative Descriptors
Use comparisons for clarity:
- "Small village, only 5-6 buildings"
- "Massive dungeon complex, cathedral-sized main chamber"

### Mood Through Color
Link mood to color explicitly:
- "Ominous atmosphere emphasized by desaturated colors and dark shadows"
- "Welcoming village with warm, bright colors"

## Example Complete Prompts

### World Map - High Fantasy
```
Epic fantasy world map on aged parchment, top-down view, three major continents connected by narrow straits, western continent with massive mountain range running north-south, central continent mostly forested with great river system, eastern continent with vast desert in south and grasslands north, oceans with decorative sea monsters, kingdoms marked with colored borders, major cities shown as small castle symbols, compass rose in corner, decorative border with fantasy motifs, warm sepia and earth tones with colored kingdom borders, hand-drawn cartography style, detailed but clear, professional atlas quality
```

### Battle Map - Forest Clearing
```
Fantasy battle map, top-down view, 40 feet by 40 feet, square grid with 5-foot squares clearly visible, forest clearing encounter, five large oak trees providing full cover positioned around edges, one fallen log across southern section for partial cover, small clear stream flowing diagonally from northwest to southeast, scattered rocks and boulders, grassy ground with dirt patches, forest visible at edges, natural daylight, high contrast for clear visibility, detailed ground textures, optimized for virtual tabletop use, game-ready asset quality
```

### Dungeon Map - Ancient Crypt
```
Fantasy dungeon map, top-down view, ancient crypt layout, entrance corridor from south leading to circular main chamber, six alcoves around main chamber containing sarcophagi, raised central platform with primary tomb, two side passages leading to treasure rooms, secret door in northeast alcove, stone walls shown thick and solid, stone tile floor with age details, pillars supporting main chamber, doors marked clearly, square grid overlay subtle but visible, torch-lit atmosphere, classic dungeon aesthetic, clear and readable layout, old-school RPG style, detailed stonework
```

### Regional Map - Frontier Town
```
Fantasy western regional map, top-down view, frontier mining town in valley center, surrounding rocky hills with visible mine entrances, single main road entering from south, small river flowing from eastern hills through town, wooden buildings in town cluster, outlying cabins scattered in hills, old abandoned mine to north marked with warning signs, forest beginning on eastern edge, clear trails connecting locations, illustrated adventure map style, warm dusty colors with green forest accents, clear details, sense of frontier isolation
```

## Template Checklist

When creating a prompt, ensure you have:
- [ ] Map type specified (world/regional/battle/dungeon)
- [ ] Perspective stated (top-down/isometric)
- [ ] Key elements listed (what's on the map)
- [ ] Style descriptor (parchment/tactical/illustrated/etc)
- [ ] Scale appropriate to map type
- [ ] Grid mentioned if needed for gameplay
- [ ] Color scheme specified
- [ ] Atmosphere/mood included
- [ ] Quality tags added
- [ ] No contradictory elements

## Quick Reference: Element Keywords

**Terrain:** mountains, hills, forest, plains, desert, tundra, swamp, ocean, river, lake, coast, cliffs, valley, canyon, plateau

**Structures:** castle, tower, fort, village, town, city, ruins, temple, dungeon, cave, mine, bridge, wall, gate

**Features:** road, path, trail, border, clearing, grove, field, farm, dock, port, camp

**Conditions:** ancient, ruined, pristine, weathered, abandoned, thriving, fortified, hidden, sacred, cursed

**Materials:** stone, wood, metal, crystal, earth, ice, lava, water

**Grid Types:** square grid, hex grid, hexagonal grid, 5-foot squares, 1-meter squares, grid overlay

**Perspectives:** top-down view, bird's eye view, isometric view, 3/4 view, overhead view
