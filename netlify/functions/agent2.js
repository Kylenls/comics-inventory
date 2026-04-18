const Anthropic = require('@anthropic-ai/sdk');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_KEY });

const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK_MARKET;

async function postToDiscord(message) {
  if (!DISCORD_WEBHOOK) return;
  await fetch(DISCORD_WEBHOOK, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: message })
  });
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

    if (action === 'market_check') {
      const { titles, publisher, year } = body;
      const prompt = `You are Taskmaster, an eBay comic book market analyst for ARC2 Comics.

Research current eBay market data for these comic titles:
${titles.join('\n')}
Publisher: ${publisher || 'Unknown'}
Year: ${year || '2026'}

For each title, provide:
1. Estimated current selling price range on eBay
2. Demand level (High/Medium/Low)
3. Recent sales velocity
4. Key selling points

Format as JSON array with fields: title, priceRange, demand, velocity, sellingPoints`;

      const response = await client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }]
      });

      let results = [];
      try {
        const text = response.content[0].text;
        const jsonMatch = text.match(/\[[\s\S]*\]/);
        if (jsonMatch) results = JSON.parse(jsonMatch[0]);
      } catch (e) {
        results = [{ title: titles[0], priceRange: 'Check eBay', demand: 'Medium', velocity: 'Normal', sellingPoints: [] }];
      }

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true, results })
      };
    }

    if (action === 'build_draft') {
      const { bundleId, seriesTitle, issue, publisher, coverList, costBasis, variantDescription, pricingMode, marketData } = body;

      const shippingTiers = [
        { max: 5, cost: 9.99 },
        { max: 10, cost: 14.99 },
        { max: 19, cost: 17.99 },
        { max: Infinity, cost: 19.99 }
      ];

      const coverCount = (coverList || '').split(',').length;
      const shipping = shippingTiers.find(t => coverCount <= t.max)?.cost || 19.99;
      const bagboard = coverCount * 0.15;
      const totalCost = parseFloat(costBasis) + bagboard;
      const breakEven = ((totalCost + shipping) / 0.87).toFixed(2);

      const prompt = `You are Taskmaster, eBay listing specialist for ARC2 Comics (Aged Readers Comics Collective).

Build an eBay bundle listing for:
Series: ${seriesTitle} #${issue}
Publisher: ${publisher || 'Unknown'}
Covers: ${coverList}
${variantDescription ? 'Special variants: ' + variantDescription : ''}
Cost basis: $${costBasis}
Break-even price: $${breakEven}
Pricing mode: ${pricingMode === 'cost_plus' ? 'Cover Costs +10%' : 'Market Price ($1 under lowest comp)'}
${marketData && marketData.length > 0 ? 'Market data: ' + JSON.stringify(marketData[0]) : ''}

Rules:
- Title max 80 characters
- Free shipping always (baked into price)
- eBay fee is 13%
- Ratio variant premiums: 1:10=$9.99, 1:25=$14.99, 1:50=$30, 1:100=$45
- Never be highest price in market

Respond with JSON only:
{
  "title": "eBay listing title max 80 chars",
  "price": 00.00,
  "breakEven": "${breakEven}",
  "margin": 00.00,
  "description": "2-3 sentence listing description",
  "reasoning": "Why this price"
}`;

      const response = await client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }]
      });

      let draft = {};
      try {
        const text = response.content[0].text;
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (jsonMatch) draft = JSON.parse(jsonMatch[0]);
      } catch (e) {
        draft = {
          title: `${seriesTitle} #${issue} Complete Cover Set ${coverList}`,
          price: parseFloat(breakEven) * 1.1,
          breakEven,
          margin: (parseFloat(breakEven) * 0.1).toFixed(2),
          description: 'Complete cover variant set. All books Near Mint. Free shipping.',
          reasoning: 'Priced at break-even +10%'
        };
      }

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true, draft, bundleId })
      };
    }

    if (action === 'publish_draft') {
      const { draft, extraContext, collageImage } = body;
      await postToDiscord(`⚔️ **Taskmaster** — Draft listing ready for review:\n**${draft.title}**\nPrice: $${draft.price} | Break-even: $${draft.breakEven} | Margin: $${draft.margin}\n${draft.description}`);
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true, message: 'Draft posted to Discord' })
      };
    }

    if (action === 'get_listings') {
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true, listings: [] })
      };
    }

    return {
      statusCode: 400, headers,
      body: JSON.stringify({ error: 'Unknown action: ' + action })
    };

  } catch (e) {
    console.error('agent2 error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
}