const Anthropic = require('@anthropic-ai/sdk');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_KEY });

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    const { imageBase64, mediaType } = JSON.parse(event.body || '{}');

    if (!imageBase64) {
      return {
        statusCode: 400, headers,
        body: JSON.stringify({ error: 'No image provided' })
      };
    }

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image',
            source: {
              type: 'base64',
              media_type: mediaType || 'image/jpeg',
              data: imageBase64
            }
          },
          {
            type: 'text',
            text: `Analyze this comic book cover and extract the following information. Respond with JSON only:
{
  "series": "series name without issue number",
  "issue": "issue number only (digits)",
  "variant": "single letter variant code (A, B, C etc) if visible",
  "variantDescription": "artist name and variant description",
  "publisher": "publisher name",
  "coverPrice": "price as number without $ sign",
  "printRun": "1st Print or 2nd Print etc if visible",
  "supplementCode": "any supplement barcode info",
  "confidence": "high/medium/low"
}

If you cannot determine a field, use null. Do not guess.`
          }
        ]
      }]
    });

    let result = {};
    try {
      const text = response.content[0].text;
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) result = JSON.parse(jsonMatch[0]);
    } catch (e) {
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ error: 'Could not parse cover data' })
      };
    }

    return {
      statusCode: 200, headers,
      body: JSON.stringify(result)
    };

  } catch (e) {
    console.error('scancover error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
}