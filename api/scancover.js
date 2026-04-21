const Anthropic = require('@anthropic-ai/sdk');
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_KEY });

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  };
  if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };

  try {
    const { imageBase64, mediaType } = JSON.parse(event.body || '{}');
    if (!imageBase64) return { statusCode: 400, headers, body: JSON.stringify({ error: 'No image provided' }) };

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image',
            source: { type: 'base64', media_type: mediaType || 'image/jpeg', data: imageBase64 }
          },
          {
            type: 'text',
            text: `You are a comic book expert. Read ALL text on this cover carefully including small print.

Extract these fields precisely:

SERIES: Main title only. No issue number. No volume number.
Good: "Amazing Spider-Man" / Bad: "Amazing Spider-Man #300"

ISSUE: Number after # symbol. Digits only. No # symbol.
Good: "14" / Bad: "#14"

VARIANT: Look for "CVR A" "CVR B" "COVER A" etc near barcode or corners.
Return single letter only: "A" "B" "C" etc. Return null if not found.

VARIANT DESCRIPTION: Artist name for this specific cover. Small text near bottom/corner.
Example: "Nick Robles Variant" or "Jae Lee Cover" or "1:10 Incentive Variant"

PUBLISHER: Marvel / DC / Image / IDW / BOOM! / Dark Horse / Titan / Mad Cave / Vault / Oni / Dynamite / Other

COVER PRICE: Dollar amount near barcode. Modern comics: $3.99 to $9.99.
Return digits only: "3.99" not "$3.99"

Rules:
- "OF 4" means 4-issue series, NOT issue 4
- Variant letter is near barcode, NOT the issue number  
- If unsure about variant, return null
- Look at ALL corners and edges for small text

Respond with JSON only:
{
  "series": "series name",
  "issue": "number",
  "variant": "letter or null",
  "variantDescription": "description or null",
  "publisher": "publisher",
  "coverPrice": "price",
  "printRun": "1st Print or null",
  "confidence": "high or medium or low"
}`
          }
        ]
      }]
    });

    let result = {};
    try {
      const text = response.content[0].text;
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) result = JSON.parse(jsonMatch[0]);
    } catch(e) {
      return { statusCode: 200, headers, body: JSON.stringify({ error: 'Could not parse cover data' }) };
    }

    return { statusCode: 200, headers, body: JSON.stringify(result) };

  } catch(e) {
    console.error('scancover error:', e);
    return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
  }
};