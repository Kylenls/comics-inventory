const Anthropic = require('@anthropic-ai/sdk');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_KEY });
const DISCORD_WEBHOOK_MARKET = process.env.DISCORD_WEBHOOK_MARKET;
const DISCORD_WEBHOOK_LISTINGS = process.env.DISCORD_WEBHOOK_LISTINGS;

async function postToDiscord(webhook, message) {
  if (!webhook) return;
  try {
    await fetch(webhook, {
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
      const { comics, count, mode, coverPriceTotal } = body;
      const comicCount = parseInt(count) || 1;

      let shippingCost;
      let shippingNote;
      if (comicCount <= 9) {
        shippingCost = 12.99;
        shippingNote = '1-9 comics: $12.99';
      } else if (comicCount <= 15) {
        shippingCost = 15.99;
        shippingNote = '10-15 comics: $15.99';
      } else if (comicCount <= 25) {
        shippingCost = 19.99;
        shippingNote = '15-25 comics: $19.99';
      } else {
        shippingCost = 0;
        shippingNote = '25+ comics: custom shipping required';
      }

      const bagBoard = comicCount * 0.15;
      const coverPrice = parseFloat(coverPriceTotal) || (comicCount * 3.99);

      const breakEven = (shippingCost + bagBoard + coverPrice) / 0.87;
      const floor = (breakEven * 1.05).toFixed(2);
      const target = (breakEven * 1.10).toFixed(2);

      const prompt = `You are Taskmaster, an expert eBay comic book seller for ARC2 (Aged Readers Comics Collective). Write a highly optimized eBay listing.

Comics to list:
${comics}

Listing type: ${mode === 'single' ? 'Single issue' : 'Bundle of ' + comicCount + ' comics'}

PRICING (already calculated for you):
- Shipping cost (baked into free shipping price): $${shippingCost.toFixed(2)} (${shippingNote})
- Bag and board: $${bagBoard.toFixed(2)}
- Cover price total: $${coverPrice.toFixed(2)}
- Break-even listing price: $${breakEven.toFixed(2)}
- Floor price (5% margin minimum): $${floor}
- Target price (10% margin): $${target}
- Use target price unless you know market data suggests higher
- Price must end in .99 or .95
- All listings show FREE SHIPPING

LISTING RULES:
- Title: max 80 characters, keyword-rich
- Include: series name, issue #, variant letters, key issue status if applicable, NM condition, publisher
- Power keywords: LOT SET RUN VARIANT 1ST KEY NM UNREAD HTF RATIO
- If ratio variants are listed (1:10, 1:25 etc) — highlight them prominently in title and description
- Description: 4 paragraphs:
  1. What's in this listing and why it's valuable/collectible
  2. Variant details and any key issue significance
  3. Condition: brand new, unread, individually bagged and boarded day of receipt
  4. Shipping: free shipping, rigid mailer, same or next business day dispatch

Return ONLY a JSON object with no other text:
{
  "title": "listing title max 80 chars",
  "price": ${target},
  "description": "full 4 paragraph description",
  "keywords": ["keyword1", "keyword2"],
  "keyIssueNotes": "any key issue or variant significance",
  "pricingRationale": "break_even=$${breakEven.toFixed(2)}, floor=$${floor}, target=$${target}, final=based on target"
}`;

      const message = await client.messages.create({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 1500,
        messages: [{ role: 'user', content: prompt }]
      });

      const text = message.content[0].text;
      let listing;
      try {
        const clean = text.trim().replace(/```json\n?/g, '').replace(/```\n?/g, '');
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

      await postToDiscord(
        DISCORD_WEBHOOK_LISTINGS,
        `🏷️ **New Listing Draft — ARC2**\n` +
        `Title: ${listing.title}\n` +
        `Price: $${listing.price} (free shipping)\n` +
        `Comics: ${comicCount} | ${shippingNote}\n` +
        `Pricing: ${listing.pricingRationale || 'see app'}\n` +
        `${listing.keyIssueNotes ? 'Key issue: ' + listing.keyIssueNotes : ''}`
      );

      return { statusCode: 200, headers, body: JSON.stringify({ ...listing, success: true }) };
    }

    if (action === 'publish_listing') {
      const { title, price } = body;
      await postToDiscord(
        DISCORD_WEBHOOK_LISTINGS,
        `📦 **Listing Published to eBay**\nTitle: ${title}\nPrice: $${price} (free shipping)`
      );
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