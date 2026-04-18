const Anthropic = require('@anthropic-ai/sdk');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_KEY });
const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK_INVENTORY;

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
    const { focDate, totalTitles, periodicals, incentives, pubBreakdown,
            sampleTitles, postToDiscord: shouldPost, signals, cashPosition } = body;

    if (shouldPost && signals) {
      const buys = signals.filter(s => s.signal === 'BUY');
      const watches = signals.filter(s => s.signal === 'WATCH');
      const totalCost = signals.reduce((s, r) => s + (parseFloat(r.cost) || 0), 0);
      const totalReturn = signals.reduce((s, r) => s + (parseFloat(r.expectedReturn) || 0), 0);

      let msg = `🔮 **Oracle — FOC Analysis${focDate ? ' — Deadline: ' + focDate : ''}**\n\n`;
      msg += `📊 **Summary:** ${buys.length} Buy · ${watches.length} Watch · ${signals.filter(s => s.signal === 'SKIP').length} Skip\n`;
      msg += `💰 Estimated spend: $${totalCost.toFixed(2)} → Est. return: $${totalReturn.toFixed(2)}\n\n`;

      if (buys.length) {
        msg += `**🟢 BUY SIGNALS:**\n`;
        buys.forEach(s => {
          msg += `• **${s.title}** — ${s.reason}`;
          if (s.qty) msg += ` (${s.qty} copies)`;
          if (s.cost) msg += ` | Cost: $${parseFloat(s.cost).toFixed(2)}`;
          msg += '\n';
        });
      }

      if (watches.length) {
        msg += `\n**🟡 WATCH:**\n`;
        watches.slice(0, 5).forEach(s => {
          msg += `• **${s.title}** — ${s.reason}\n`;
        });
      }

      await postToDiscord(msg);
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true })
      };
    }

    const bank = cashPosition?.bank || 0;
    const ebayPending = cashPosition?.ebayPending || 0;
    const whatnotPending = cashPosition?.whatnotPending || 0;
    const focDue = cashPosition?.focDue || 0;
    const projected = bank + ebayPending + whatnotPending;
    const spendable = Math.max(0, projected - 200 - focDue);
    const focBudget = Math.round(spendable * 0.40 * 100) / 100;

    const prompt = `You are Oracle, the market intelligence agent for ARC2 Comics (Aged Readers Comics Collective).

Your North Star: Grow ARC2's buying budget through smart market decisions.

Analyze this FOC catalog and provide buy/watch/skip signals:

FOC Date: ${focDate || 'This week'}
Total titles: ${totalTitles}
Single issues: ${periodicals}
Incentive variants: ${incentives}
Publishers: ${pubBreakdown}

Available FOC budget: $${focBudget.toFixed(2)}

Titles to analyze:
${sampleTitles}

For each title evaluate:
- First appearances or key issues
- Creator heat (popular artists/writers)
- Movie/TV crossovers or announcements  
- Publisher momentum
- Ratio variant investment potential
- Your own sales history context

Respond with JSON only — an array of signals:
[
  {
    "title": "exact title",
    "signal": "BUY" or "WATCH" or "SKIP",
    "reason": "concise reason",
    "strategy": "how to sell it",
    "qty": 0,
    "cost": 0.00,
    "expectedReturn": 0.00,
    "confidence": 0
  }
]

Only include BUY and WATCH signals — skip the SKIPs to keep it focused.
Total BUY cost must not exceed $${focBudget.toFixed(2)}.`;

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{ role: 'user', content: prompt }]
    });

    let signals_result = [];
    let totalCost = 0;
    let totalReturn = 0;

    try {
      const text = response.content[0].text;
      const jsonMatch = text.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        signals_result = JSON.parse(jsonMatch[0]);
        totalCost = signals_result.reduce((s, r) => s + (parseFloat(r.cost) || 0), 0);
        totalReturn = signals_result.reduce((s, r) => s + (parseFloat(r.expectedReturn) || 0), 0);
      }
    } catch (e) {
      console.error('Parse error:', e);
    }

    return {
      statusCode: 200, headers,
      body: JSON.stringify({
        success: true,
        signals: signals_result,
        totalCost,
        totalReturn,
        focBudget
      })
    };

  } catch (e) {
    console.error('analyzefoc error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};