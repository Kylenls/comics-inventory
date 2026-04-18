const Anthropic = require('@anthropic-ai/sdk');
const Airtable = require('airtable');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_KEY });
const base = new Airtable({ apiKey: process.env.AIRTABLE_TOKEN }).base(process.env.AIRTABLE_BASE);

const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK_INVENTORY;
const CASH_TABLE = 'tblZ4JKl5J2SHdxak';
const INV_TABLE = 'tbl9SzUrvBcAz74BL';

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
    // Get cash position
    const cashRecords = await base(CASH_TABLE).select({ maxRecords: 1 }).firstPage();
    const cash = cashRecords[0]?.fields || {};
    const bank = parseFloat(cash['Bank Balance'] || 0);
    const ebayPending = parseFloat(cash['eBay Pending'] || 0);
    const whatnotPending = parseFloat(cash['Whatnot Pending'] || 0);
    const focDue = parseFloat(cash['FOC Due This Week'] || 0);
    const projected = bank + ebayPending + whatnotPending;
    const spendable = Math.max(0, projected - 200 - focDue);
    const focBudget = Math.round(spendable * 0.40 * 100) / 100;

    // Get inventory snapshot
    const invRecords = await base(INV_TABLE).select({
      maxRecords: 100,
      filterByFormula: "OR({Status}='In Stock', {Status}='Ordered')",
      fields: ['Series', 'Issue', 'Variant', 'Publisher', 'Status', 'Purchase Price']
    }).firstPage();

    const totalInStock = invRecords.filter(r => r.fields['Status'] === 'In Stock').length;
    const totalOrdered = invRecords.filter(r => r.fields['Status'] === 'Ordered').length;

    const prompt = `You are Oracle, the market intelligence agent for ARC2 Comics (Aged Readers Comics Collective), a comic book business run by Kyle and Justin in Phoenix, AZ.

Your North Star: Grow ARC2's buying budget through smart market decisions. Earn full purchasing autonomy.

Current financial position:
- Bank balance: $${bank.toFixed(2)}
- eBay pending: $${ebayPending.toFixed(2)}
- Whatnot pending: $${whatnotPending.toFixed(2)}
- Projected total: $${projected.toFixed(2)}
- FOC due this week: $${focDue.toFixed(2)}
- Available FOC budget (40% of spendable): $${focBudget.toFixed(2)}

Current inventory:
- ${totalInStock} comics in stock
- ${totalOrdered} comics on order

Deliver a Monday morning FOC briefing for Kyle and Justin. Include:
1. Cash position summary and what it means for buying
2. Market intelligence — what's trending in comics right now, first appearances, movie/TV announcements, hot artists
3. 3-5 specific buying recommendations with reasoning and confidence scores
4. What to watch out for this week
5. Any adjacent collectible opportunities

Be chatty, confident, and proactive. This is your weekly moment to shine. Sign off as 🔮 Oracle.`;

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{ role: 'user', content: prompt }]
    });

    const briefing = response.content[0].text;
    await postToDiscord(`🔮 **Oracle — Monday FOC Briefing**\n\n${briefing}`);

    return {
      statusCode: 200, headers,
      body: JSON.stringify({ success: true, focBudget, briefing })
    };

  } catch (e) {
    console.error('agent1 error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};