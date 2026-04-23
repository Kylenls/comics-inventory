const Airtable = require('airtable');

const base = new Airtable({ apiKey: process.env.AIRTABLE_TOKEN }).base(process.env.AIRTABLE_BASE);
const TABLE = process.env.AIRTABLE_TABLE || 'tbl9SzUrvBcAz74BL';
const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK_INVENTORY;

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

async function getNextSkuNum() {
  let maxNum = 0;
  await new Promise((resolve, reject) => {
    base(TABLE).select({
      filterByFormula: "LEFT({SKU}, 4) = 'COM-'",
      fields: ['SKU']
    }).eachPage((records, fetchNextPage) => {
      records.forEach(r => {
        const num = parseInt((r.fields['SKU'] || '').replace('COM-', '')) || 0;
        if (num > maxNum) maxNum = num;
      });
      fetchNextPage();
    }, (err) => { if (err) reject(err); else resolve(); });
  });
  return maxNum + 1;
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
    const { items, invoiceNumber, invoiceDate, source } = JSON.parse(event.body || '{}');
    if (!items || !items.length) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'No items provided' }) };
    }

    // Block duplicate invoice imports
    if (invoiceNumber) {
      const dupeCheck = await base(TABLE).select({
        filterByFormula: `{Invoice Number}="${invoiceNumber}"`,
        maxRecords: 1,
        fields: ['SKU']
      }).firstPage();
      if (dupeCheck.length > 0) {
        return {
          statusCode: 400, headers,
          body: JSON.stringify({
            error: `Invoice #${invoiceNumber} already exists (${dupeCheck[0].fields['SKU']}). Import cancelled to prevent duplicates.`
          })
        };
      }
    }

    // Get true next SKU - scans entire table
    let nextSkuNum = await getNextSkuNum();

    let created = 0;
    let errors = 0;
    let firstSku = null;
    let lastSku = null;
    const publishers = {};

    for (const item of items) {
      for (let i = 0; i < (item.qty || 1); i++) {
        const sku = `COM-${String(nextSkuNum).padStart(5, '0')}`;
        if (!firstSku) firstSku = sku;
        lastSku = sku;
        nextSkuNum++;

        if (item.publisher) {
          publishers[item.publisher] = (publishers[item.publisher] || 0) + 1;
        }

        const fields = {
          'SKU': sku,
          'Series': item.series || '',
          'Issue': item.issue || '',
          'Variant': item.variant || '',
          'Variant Description': item.variantDescription || '',
          'Publisher': item.publisher || '',
          'Cover Price': parseFloat(item.coverPrice) || 0,
          'Purchase Price': parseFloat(item.purchasePrice) || 0,
          'Bag Board': 0.15,
          'Status': 'Ordered',
          'Condition': 'Brand New',
          'Source': source === 'LunarCSV' ? 'Lunar Distribution' : source || '',
          'Invoice Number': invoiceNumber || '',
          'UPC': item.upc || '',
          'Lunar Code': item.lunarCode || '',
          'Added Date': new Date().toISOString().split('T')[0],
          'Oracle Signal': 'Pre-Oracle',
          'KJ Decision': 'Pre-Oracle'
        };

        if (invoiceDate) fields['Order Date'] = invoiceDate;

        try {
          await base(TABLE).create(fields);
          created++;
        } catch(e) {
          console.error('Create error:', e.message);
          errors++;
        }

        await new Promise(r => setTimeout(r, 80));
      }
    }

    const totalCost = items.reduce((sum, item) => sum + ((item.purchasePrice || 0) * (item.qty || 1)), 0);
    const pubBreakdown = Object.entries(publishers).map(([p, n]) => `${p}: ${n}`).join(', ');
    const distributor = source === 'LunarCSV' ? 'Lunar Distribution' : source || 'Unknown';

    await postToDiscord(
      `📦 **New Invoice Imported**\n` +
      `Invoice #${invoiceNumber || 'N/A'} — ${distributor}\n` +
      `📅 Order Date: ${invoiceDate || 'N/A'}\n` +
      `📚 ${created} comics added\n` +
      `💰 Total cost: $${totalCost.toFixed(2)}\n` +
      `🏷️ SKUs: ${firstSku} → ${lastSku}\n` +
      `📊 Publishers: ${pubBreakdown || 'N/A'}\n` +
      (errors > 0 ? `⚠️ ${errors} errors\n` : '') +
      `👁️ Watcher — please update cash flow and inventory counts.`
    );

    return {
      statusCode: 200, headers,
      body: JSON.stringify({ success: true, created, errors, firstSku, lastSku })
    };

  } catch(e) {
    console.error('importinvoice error:', e);
    return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
  }
};