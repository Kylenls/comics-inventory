const Airtable = require('airtable');

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
    const { filename, content, distributor } = JSON.parse(event.body || '{}');
    if (!filename || !content) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'Missing data' }) };
    }

    const base = new Airtable({ apiKey: process.env.AIRTABLE_TOKEN }).base(process.env.AIRTABLE_BASE);
    
    await base('tbl4sAX5BbnjkJZLv').create({
      'Filename': filename,
      'Content': content,
      'Distributor': distributor || 'Lunar',
      'Status': 'Pending',
      'Uploaded At': new Date().toISOString().split('T')[0]
    });

    return {
      statusCode: 200, headers,
      body: JSON.stringify({ success: true, message: 'FOC queued for Oracle' })
    };

  } catch (e) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
  }
};