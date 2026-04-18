with open('/Users/kylenelson/arc2-comics/netlify/functions/scancover.js', 'r') as f:
    content = f.read()

old_prompt = '''text: `You are analyzing a comic book cover for inventory purposes. Extract every piece of text visible on this cover carefully.'''

new_prompt = '''text: `You are a comic book expert analyzing a cover image for inventory data entry. Be extremely precise.

STEP 1 - Read ALL text visible on the cover, no matter how small.
STEP 2 - Extract these specific fields:

SERIES NAME: The main title. Usually largest text. Do NOT include issue number or volume.
Examples: "Amazing Spider-Man", "Batman", "Absolute Flash", "Corpse Knight"

ISSUE NUMBER: Look for # followed by digits. Examples: #1, #14, #300
Just return the digits, no # symbol.

VARIANT LETTER: Look carefully for:
- Text saying "CVR A", "CVR B", "COVER A", "COVER B" 
- A single letter near the barcode area
- Small text in corners
This is critical — look very carefully. Return single letter only.

VARIANT DESCRIPTION: Artist name for this cover. Usually small text near bottom or corner.
Examples: "Nick Robles Variant", "Jae Lee Cover", "Incentive 1:10 Variant"

PUBLISHER: Look for publisher logo/name. Usually Marvel, DC, Image, IDW, BOOM!, Dark Horse, Titan, Mad Cave, Vault, Oni Press, Dynamite.

COVER PRICE: Look near barcode for price like $3.99, $4.99, $5.99, $6.99, $7.99, $8.99

IMPORTANT:
- If you see "OF 4", "OF 6" etc that is the series length, not the issue number
- Variant letter is NOT the same as issue number
- If unsure about variant letter, return null rather than guessing
- Cover price for modern comics is almost always between $3.99 and $9.99

Return JSON only, no explanation:
{
  "series": "exact series name",
  "issue": "digits only",
  "variant": "single letter or null",
  "variantDescription": "artist and description or null",
  "publisher": "publisher name",
  "coverPrice": "decimal number only",
  "printRun": "1st Print or null",
  "confidence": "high or medium or low"
}`'''

if 'You are analyzing a comic book cover' in content:
    # Find the full old prompt
    start = content.find("text: `You are analyzing")
    end = content.find('`\n          }\n        ]\n      }]\n    })')
    if start > 0 and end > 0:
        old_block = content[start:end]
        content = content.replace(old_block, new_prompt, 1)
        print("Prompt updated successfully")
    else:
        print(f"Could not find prompt boundaries: start={start} end={end}")
else:
    print("Old prompt not found")

with open('/Users/kylenelson/arc2-comics/netlify/functions/scancover.js', 'w') as f:
    f.write(content)