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
    const { items, invoiceNumber, invoiceDate, source } = JSON.parse(event.body || '{}');
    if (!items || !items.length) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'No items provided' }) };
    }

    // Get next SKU number
    const existing = await base(TABLE).select({
      sort: [{ field: 'SKU', direction: 'desc' }],
      maxRecords: 1,
      fields: ['SKU']
    }).firstPage();

    let nextSkuNum = 1;
    if (existing.length > 0) {
      const lastSku = existing[0].fields['SKU'] || 'COM-00000';
      nextSkuNum = (parseInt(lastSku.replace('COM-', '')) || 0) + 1;
    }

    let created = 0;
    let errors = 0;
    let firstSku = null;
    let lastSku = null;

    for (const item of items) {
      for (let i = 0; i < (item.qty || 1); i++) {
        const sku = `COM-${String(nextSkuNum).padStart(5, '0')}`;
        if (!firstSku) firstSku = sku;
        lastSku = sku;
        nextSkuNum++;

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
          'Added Date': new Date().toISOString().split('T')[0]
        };

        if (invoiceDate) fields['Order Date'] = invoiceDate;

        try {
          await base(TABLE).create(fields);
          created++;
        } catch (e) {
          console.error('Create error:', e.message);
          errors++;
        }

        await new Promise(r => setTimeout(r, 80));
      }
    }

    return {
      statusCode: 200, headers,
      body: JSON.stringify({ success: true, created, errors, firstSku, lastSku })
    };

  } catch (e) {
    console.error('importinvoice error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};