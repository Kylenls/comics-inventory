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
    const { pdfBase64 } = JSON.parse(event.body || '{}');

    if (!pdfBase64) {
      return {
        statusCode: 400, headers,
        body: JSON.stringify({ error: 'No PDF provided' })
      };
    }

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4000,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'document',
            source: {
              type: 'base64',
              media_type: 'application/pdf',
              data: pdfBase64
            }
          },
          {
            type: 'text',
            text: `This is a Lunar Distribution invoice PDF. Extract all ordered comic book line items.

For each line item extract:
- series name (without issue number)
- issue number
- variant letter (A, B, C etc from CVR X)
- variant description (artist name etc)
- quantity ordered (Qty column)
- retail price
- discounted price (what ARC2 pays)
- UPC code
- Lunar item code
- publisher

Also extract the invoice number and invoice date from the header.

Respond with JSON only:
{
  "invoiceNumber": "number",
  "invoiceDate": "YYYY-MM-DD",
  "items": [
    {
      "series": "",
      "issue": "",
      "variant": "",
      "variantDescription": "",
      "qty": 0,
      "coverPrice": 0.00,
      "purchasePrice": 0.00,
      "upc": "",
      "lunarCode": "",
      "publisher": ""
    }
  ],
  "totalSkus": 0
}

Only include items with qty > 0. Skip promotional items with $0 price.`
          }
        ]
      }]
    });

    let result = { items: [], totalSkus: 0 };
    try {
      const text = response.content[0].text;
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        result = JSON.parse(jsonMatch[0]);
        if (!result.totalSkus) {
          result.totalSkus = result.items.reduce((s, i) => s + (i.qty || 0), 0);
        }
      }
    } catch (e) {
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ error: 'Could not parse invoice data' })
      };
    }

    return {
      statusCode: 200, headers,
      body: JSON.stringify(result)
    };

  } catch (e) {
    console.error('parselunar error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};