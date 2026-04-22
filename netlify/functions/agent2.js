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
      const { comics, count, mode, comicDetails, coverPriceTotal } = body;

      const comicCount = parseInt(count) || 1;

      // Shipping tier based on comic count
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
      const ebayFeeRate = 0.13;

      const prompt = `You are Taskmaster, an expert eBay comic book seller for ARC2 (Aged Readers Comics Collective). Your job is to write highly optimized eBay listings and set profitable, competitive prices.

Comics to list:
${comics}

${comicDetails ? 'Additional details from inventory:\n' + comicDetails : ''}

Listing type: ${mode === 'single' ? 'Single issue' : 'Bundle of ' + comicCount + ' comics'}
Comic count: ${comicCount}

STEP 1 - RESEARCH (use web search):
- Search eBay SOLD listings (not active) for each comic in the last 90 days
- Note the median sold price and price range for comparable NM copies
- Find if any are key issues (first appearances, deaths, major events, origin stories)
- Find variant significance (ratio variants 1:10, 1:25, 1:50 command premiums)
- Note keywords from highest-performing sold listings

STEP 2 - PRICING CALCULATION:
Our costs (already calculated for you):
- Shipping + label (baked into "free shipping" price): $${shippingCost.toFixed(2)} (${shippingNote})
- Bag and board: $${bagBoard.toFixed(2)} ($0.15 x ${comicCount} comics)
- eBay fee: 13% of final sale price
${coverPriceTotal ? '- Total cover price of comics: $' + coverPriceTotal : '- Note: cover price total not provided, estimate from comic details'}

Calculate break-even listing price:
  break_even = (shipping + bag_board + cover_price_total) / (1 - 0.13)

Then calculate:
  floor_price = break_even * 1.05  (minimum 5% margin - do not go below this)
  target_price = break_even * 1.10  (standard 10% margin)

Pricing decision:
- Search eBay sold listings for median sold price
- market_price = median_sold * 0.97  (3% below median to be most competitive)
- IF market_price > target_price: use market_price (take the higher margin)
- IF market_price is between floor and target: use target_price
- IF market_price < floor_price OR no market data found: use target_price
- NEVER go below floor_price
- ${comicCount > 25 ? 'FLAG: This bundle requires custom shipping quote - do not calculate shipping into price' : ''}
- Price should end in .99 or .95

STEP 3 - WRITE THE LISTING:
All listings show FREE SHIPPING - shipping cost is baked into our price, never shown to buyer.

Title (max 80 chars):
- Lead with most valuable/recognizable comic
- Include: series, issue #, variant letter, key status, NM, publisher
- Power keywords: LOT SET RUN VARIANT 1ST KEY NM UNREAD HTF RATIO

Description (4 paragraphs):
1. What's in this listing and why it's special/valuable
2. Key issue significance or variant details  
3. Condition: brand new, unread, individually bagged and boarded
4. Shipping: free shipping, carefully packaged in a rigid mailer, same or next business day dispatch

Return ONLY a JSON object with no other text:
{
  "title": "listing title max 80 chars",
  "price": 57.99,
  "description": "full 4 paragraph description",
  "keywords": ["keyword1", "keyword2"],
  "keyIssueNotes": "key issue significance found",
  "pricingRationale": "break_even=$X, floor=$X, target=$X, market_median=$X, final=$X"
}`;

      const message = await client.messages.create({
        model: 'claude-opus-4-5',
        max_tokens: 3000,
        tools: [{ type: 'web_search_20250305', name: 'web_search' }],
        messages: [{ role: 'user', content: prompt }]
      });

      let text = '';
      for (const block of message.content) {
        if (block.type === 'text') text += block.text;
      }

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
        `🏷️ **New Listing Draft — ARC2**\n` +
        `Title: ${listing.title}\n` +
        `Price: $${listing.price} (free shipping)\n` +
        `Comics: ${comicCount} | Shipping tier: ${shippingNote}\n` +
        `Pricing: ${listing.pricingRationale || 'see app'}\n` +
        `${listing.keyIssueNotes ? 'Key issue: ' + listing.keyIssueNotes : ''}`
      );

      return { statusCode: 200, headers, body: JSON.stringify({ ...listing, success: true }) };
    }

    if (action === 'publish_listing') {
      const { title, price, description } = body;
      await postToDiscord(`📦 **Listing Published to eBay**\nTitle: ${title}\nPrice: $${price} (free shipping)`);
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