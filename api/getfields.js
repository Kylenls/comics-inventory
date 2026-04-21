const Airtable = require('airtable');

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    const base = new Airtable({ apiKey: process.env.AIRTABLE_TOKEN }).base(process.env.AIRTABLE_BASE);
    const records = await base(process.env.AIRTABLE_TABLE || 'tbl9SzUrvBcAz74BL')
      .select({ maxRecords: 1 }).firstPage();

    const fields = records.length > 0 ? Object.keys(records[0].fields) : [];

    return {
      statusCode: 200, headers,
      body: JSON.stringify({ fields })
    };
  } catch (e) {
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};