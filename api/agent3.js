const Anthropic = require('@anthropic-ai/sdk');
const Airtable = require('airtable');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_KEY });
const base = new Airtable({ apiKey: process.env.AIRTABLE_TOKEN }).base(process.env.AIRTABLE_BASE);

const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK_INVENTORY;
const INV_TABLE = 'tbl9SzUrvBcAz74BL';
const CASH_TABLE = 'tblZ4JKl5J2SHdxak';

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
    const { trigger, invoiceNumber, salePrice, platform, costBasis, bagBoard,
            labelCost, shippingCost, platformFee, netProfit, daysOnMarket,
            itemCount, bundleId, title, skus, ebaySales } = body;

    // Get inventory data
    const invRecords = await base(INV_TABLE).select({
      maxRecords: 200,
      fields: ['Series', 'Issue', 'Variant', 'Status', 'Purchase Price',
               'Sale Price', 'Sale Date', 'Sale Platform', 'Bundle ID',
               'Listed On', 'Publisher', 'Invoice Number']
    }).firstPage();

    const inStock = invRecords.filter(r => r.fields['Status'] === 'In Stock');
    const ordered = invRecords.filter(r => r.fields['Status'] === 'Ordered');
    const sold = invRecords.filter(r => r.fields['Status'] === 'Sold');

    // Get cash position
    const cashRecords = await base(CASH_TABLE).select({ maxRecords: 1 }).firstPage();
    const cash = cashRecords[0]?.fields || {};

    if (trigger === 'sale') {
      const message = `👁️ **The Watcher — Sale Logged**

**${title || bundleId || 'Item'}** ${itemCount > 1 ? `(${itemCount} comics)` : ''}
💰 Sale price: $${parseFloat(salePrice || 0).toFixed(2)} on ${platform}
📦 Cost basis: $${parseFloat(costBasis || 0).toFixed(2)} + bag/board $${parseFloat(bagBoard || 0).toFixed(2)}
🏷️ Fees: $${parseFloat(platformFee || 0).toFixed(2)} | Label: $${parseFloat(labelCost || 0).toFixed(2)} | Supplies: $${parseFloat(shippingCost || 0).toFixed(2)}
${netProfit >= 0 ? '✅' : '❌'} **Net profit: ${netProfit >= 0 ? '+' : ''}$${parseFloat(netProfit || 0).toFixed(2)}**
⏱️ Days on market: ${daysOnMarket || 0}
📊 Total sold to date: ${sold.length + 1} comics`;

      await postToDiscord(message);

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true })
      };
    }

    if (trigger === 'invoice') {
      const invoiceItems = invRecords.filter(r => r.fields['Invoice Number'] === invoiceNumber);
      await postToDiscord(`👁️ **The Watcher — New Invoice Received**\nInvoice #${invoiceNumber}: ${invoiceItems.length} comics added to inventory\nCurrent stock: ${inStock.length} in stock, ${ordered.length} on order`);

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true })
      };
    }

    if (trigger === 'daily') {
      const totalCostBasis = inStock.reduce((s, r) => s + (parseFloat(r.fields['Purchase Price']) || 0), 0);
      const recentSold = sold.slice(-10);

      const prompt = `You are The Watcher, the P&L auditor for ARC2 Comics run by Kyle and Justin.

Your North Star: Ensure Oracle and Taskmaster hit their autonomy goals by giving everyone honest data.

Current inventory snapshot:
- ${inStock.length} comics in stock (cost basis: $${totalCostBasis.toFixed(2)})
- ${ordered.length} comics on order
- ${sold.length} total sold to date

Cash position:
- Bank: $${parseFloat(cash['Bank Balance'] || 0).toFixed(2)}
- eBay pending: $${parseFloat(cash['eBay Pending'] || 0).toFixed(2)}
- Whatnot pending: $${parseFloat(cash['Whatnot Pending'] || 0).toFixed(2)}

Deliver a concise daily digest. Include:
1. Inventory health snapshot
2. Any concerns or flags
3. One actionable insight for Kyle and Justin

Be direct and data-focused. Sign off as 👁️ The Watcher.`;

      const response = await client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }]
      });

      const digest = response.content[0].text;
      await postToDiscord(`👁️ **The Watcher — Daily Digest**\n\n${digest}`);

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true, digest })
      };
    }

    if (trigger === 'weekly') {
      const prompt = `You are The Watcher, the P&L auditor for ARC2 Comics.

Current inventory:
- ${inStock.length} in stock
- ${ordered.length} on order  
- ${sold.length} total sold

Cash:
- Bank: $${parseFloat(cash['Bank Balance'] || 0).toFixed(2)}
- eBay pending: $${parseFloat(cash['eBay Pending'] || 0).toFixed(2)}

Deliver a weekly scorecard report. Include:
1. Overall business health assessment
2. Inventory turn rate analysis
3. Oracle and Taskmaster performance notes
4. Recommendations for the week ahead
5. Progress toward agent autonomy milestones

Be thorough but concise. Sign off as 👁️ The Watcher.`;

      const response = await client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }]
      });

      const report = response.content[0].text;
      await postToDiscord(`👁️ **The Watcher — Weekly Scorecard**\n\n${report}`);

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true, report })
      };
    }

    if (trigger === 'ebay_analysis') {
      const totalRevenue = (ebaySales || []).reduce((s, r) => s + (r.salePrice || 0), 0);
      await postToDiscord(`👁️ **The Watcher — eBay Sales Analysis**\n${(ebaySales || []).length} orders analyzed\nTotal revenue: $${totalRevenue.toFixed(2)}\nData logged for scorecard tracking.`);

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true })
      };
    }

    return {
      statusCode: 400, headers,
      body: JSON.stringify({ error: 'Unknown trigger: ' + trigger })
    };

  } catch (e) {
    console.error('agent3 error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};