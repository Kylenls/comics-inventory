const Airtable = require('airtable');

const base = new Airtable({ apiKey: process.env.AIRTABLE_TOKEN }).base(process.env.AIRTABLE_BASE);
const TABLE = process.env.AIRTABLE_TABLE || 'tbl9SzUrvBcAz74BL';

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
    const { sales } = JSON.parse(event.body || '{}');

    if (!sales || !sales.length) {
      return {
        statusCode: 400, headers,
        body: JSON.stringify({ error: 'No sales data provided' })
      };
    }

    let matched = 0;
    let unmatched = 0;

    for (const sale of sales) {
      try {
        const title = sale.title || '';
        const words = title.split(' ').slice(0, 3).join(' ');

        const records = await base(TABLE).select({
          filterByFormula: `AND({Status}='Listed', FIND('${words.replace(/'/g, "\\'")}', {Series}))`,
          maxRecords: 5
        }).firstPage();

        if (records.length > 0) {
          await base(TABLE).update(records[0].id, {
            'Status': 'Sold',
            'Sale Price': parseFloat(sale.salePrice) || 0,
            'Sale Date': sale.saleDate || new Date().toISOString().split('T')[0],
            'Sale Platform': 'eBay'
          });
          matched++;
        } else {
          unmatched++;
        }
      } catch (e) {
        console.error('Match error:', e.message);
        unmatched++;
      }

      await new Promise(r => setTimeout(r, 100));
    }

    return {
      statusCode: 200, headers,
      body: JSON.stringify({ success: true, matched, unmatched })
    };

  } catch (e) {
    console.error('importebay error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};