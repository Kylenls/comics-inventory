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
    const { imageBase64 } = JSON.parse(event.body || '{}');

    if (!imageBase64) {
      return {
        statusCode: 400, headers,
        body: JSON.stringify({ error: 'No image provided' })
      };
    }

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 500,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image',
            source: {
              type: 'base64',
              media_type: 'image/jpeg',
              data: imageBase64
            }
          },
          {
            type: 'text',
            text: `Read the barcode in this image. Comic book barcodes are typically UPC-A (12 digits) or EAN-13 (13 digits).

Respond with JSON only:
{
  "barcode": "the barcode digits only",
  "variant": "single letter variant if shown in supplement code",
  "printRun": "print run number if shown"
}

If you cannot read a barcode, return: {"barcode": null}`
          }
        ]
      }]
    });

    let result = { barcode: null };
    try {
      const text = response.content[0].text;
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) result = JSON.parse(jsonMatch[0]);
    } catch (e) {
      result = { barcode: null };
    }

    return {
      statusCode: 200, headers,
      body: JSON.stringify(result)
    };

  } catch (e) {
    console.error('decodebarcode error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};