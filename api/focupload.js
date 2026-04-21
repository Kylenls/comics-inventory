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
    console.log('focupload called, body length:', event.body?.length);
    
    const { filename, content, distributor } = JSON.parse(event.body || '{}');
    
    console.log('filename:', filename, 'distributor:', distributor, 'content length:', content?.length);
    
    if (!filename || !content) {
      console.log('Missing filename or content');
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'Missing data' }) };
    }

    console.log('Connecting to Airtable...');
    const base = new Airtable({ apiKey: process.env.AIRTABLE_TOKEN }).base(process.env.AIRTABLE_BASE);
    
    console.log('Creating record in FOC Queue...');
    const record = await base('tbl4sAX5BbnjkJZLv').create({
      'Filename': filename,
      'Content': content.substring(0, 100000),
      'Distributor': distributor || 'Lunar',
      'Status': 'Pending',
      'Uploaded At': new Date().toISOString().split('T')[0]
    });

    console.log('Record created:', record.id);

    return {
      statusCode: 200, headers,
      body: JSON.stringify({ success: true, message: 'FOC queued for Oracle', id: record.id })
    };

  } catch (e) {
    console.error('focupload error:', e.message, e.stack);
    return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
  }
};