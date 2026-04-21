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
    const body = JSON.parse(event.body || '{}');
    const { action } = body;

    if (action === 'generate_listing') {
      const { comics, count, mode } = body;

      const prompt = `You are Taskmaster, an expert eBay seller specializing in comic books. Your listings consistently rank at the top of search results and convert browsers into buyers.

Generate an optimized eBay listing for these comics:
${comics}

Listing type: ${mode === 'single' ? 'Single issue' : 'Bundle of ' + count + ' comics'}

eBay listing rules:
- Title max 80 characters - pack with keywords buyers search for
- Lead with the most recognizable/valuable comic in the bundle
- Include: series name, issue number, key details (first appearance, variant, ratio), condition (NM/Near Mint), publisher
- Use terms buyers search: "LOT", "RUN", "SET", "VARIANT", "1ST PRINT", "KEY ISSUE", "NM", "UNREAD"
- Description should be 3-4 paragraphs: what's in the lot, why it's valuable, condition details, shipping info
- Price using these rules: cover price × 1.8 for bundles, never be the highest price in market, account for 13% eBay fee

Pricing context:
- All comics are brand new, unread, bagged and boarded
- Free shipping always included
- eBay fee: 13%
- Bag/board cost: $0.15 per comic

Return ONLY a JSON object with no other text:
{
  "title": "eBay listing title here (max 80 chars)",
  "price": 29.99,
  "description": "Full listing description here...",
  "keywords": ["keyword1", "keyword2"]
}`;

      const message = await client.messages.create({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 1024,
        messages: [{ role: 'user', content: prompt }]
      });

      const text = message.content[0].text;
      let listing;
      try {
        const clean = text.trim().replace(/```json\n?/g, '').replace(/```\n?/g, '');
        listing = JSON.parse(clean);
      } catch(e) {
        return { statusCode: 500, headers, body: JSON.stringify({ error: 'Failed to parse listing: ' + text }) };
      }

      // Enforce 80 char title limit
      if (listing.title && listing.title.length > 80) {
        listing.title = listing.title.substring(0, 80);
      }

      return { statusCode: 200, headers, body: JSON.stringify({ ...listing, success: true }) };
    }

    if (action === 'publish_listing') {
      // eBay publish placeholder - returns success for now
      const { title, price, description } = body;
      return {
        statusCode: 200, headers,
        body: JSON.stringify({
          success: true,
          message: 'Listing queued for publish - eBay OAuth integration coming soon',
          listingId: 'PENDING-' + Date.now()
        })
      };
    }

    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Unknown action: ' + action }) };

  } catch(e) {
    console.error('agent2 error:', e);
    return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
  }
};