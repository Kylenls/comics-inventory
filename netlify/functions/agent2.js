const Anthropic = require('@anthropic-ai/sdk');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_KEY });
const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK_MARKET;

async function postToDiscord(message) {
  if (!DISCORD_WEBHOOK) return;
  try {
    await fetch(DISCORD_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: message })
    });
  } catch(e) {
    console.error('Discord error:', e.message);
  }
}

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
      const { comics, count, mode, comicDetails } = body;

      const prompt = `You are Taskmaster, an expert eBay comic book seller. Your job is to write a highly optimized eBay listing that ranks at the top of search results and converts buyers.

Comics to list:
${comics}

${comicDetails ? 'Additional details from inventory:\n' + comicDetails : ''}

Listing type: ${mode === 'single' ? 'Single issue' : 'Bundle of ' + (count || 'multiple') + ' comics'}

Instructions:
1. Use your web search tool to research each comic - find: current eBay sold prices, whether it's a key issue (first appearances, deaths, major events), variant significance, print run details, and what keywords buyers are searching for
2. After researching, write the listing

eBay listing rules:
- Title: max 80 characters, pack with searchable keywords
- Lead with most valuable/recognizable comic
- Include: series, issue, variant letter, key issue status, condition (NM), publisher
- Power keywords: LOT, RUN, SET, VARIANT, 1ST PRINT, KEY ISSUE, NM, UNREAD, HTF, RATIO
- Description: 3-4 paragraphs covering what's in the lot, why it's valuable/collectible, condition, and shipping
- Price: based on current eBay sold prices, never the highest, account for 13% eBay fee and free shipping

Condition: All comics are brand new, unread, bagged and boarded. Free shipping included.

Return ONLY a JSON object:
{
  "title": "listing title max 80 chars",
  "price": 29.99,
  "description": "full description here",
  "keywords": ["keyword1", "keyword2"],
  "keyIssueNotes": "any key issue significance found"
}`;

      const message = await client.messages.create({
        model: 'claude-opus-4-5',
        max_tokens: 2048,
        tools: [
          {
            type: 'web_search_20250305',
            name: 'web_search'
          }
        ],
        messages: [{ role: 'user', content: prompt }]
      });

      // Extract text from response (may have tool use blocks)
      let text = '';
      for (const block of message.content) {
        if (block.type === 'text') {
          text += block.text;
        }
      }

      let listing;
      try {
        const clean = text.trim().replace(/```json\n?/g, '').replace(/```\n?/g, '');
        // Find JSON in the response
        const jsonMatch = clean.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          listing = JSON.parse(jsonMatch[0]);
        } else {
          throw new Error('No JSON found');
        }
      } catch(e) {
        return { statusCode: 500, headers, body: JSON.stringify({ error: 'Failed to parse listing: ' + text.slice(0, 200) }) };
      }

      if (listing.title && listing.title.length > 80) {
        listing.title = listing.title.substring(0, 80);
      }

      await postToDiscord(`🏷️ **New Listing Draft**\nTitle: ${listing.title}\nPrice: $${listing.price}\n${listing.keyIssueNotes ? 'Key: ' + listing.keyIssueNotes : ''}`);

      return { statusCode: 200, headers, body: JSON.stringify({ ...listing, success: true }) };
    }

    if (action === 'publish_listing') {
      const { title, price, description } = body;
      await postToDiscord(`📦 **Listing Published**\nTitle: ${title}\nPrice: $${price}`);
      return {
        statusCode: 200, headers,
        body: JSON.stringify({
          success: true,
          message: 'Listing queued - eBay OAuth integration coming soon',
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