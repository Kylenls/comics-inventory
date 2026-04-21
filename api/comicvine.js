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
    const { action, barcode, series, issue } = JSON.parse(event.body || '{}');
    const API_KEY = process.env.COMICVINE_KEY;
    const BASE_URL = 'https://comicvine.gamespot.com/api';

    if (action === 'barcode') {
      const url = `${BASE_URL}/issues/?api_key=${API_KEY}&format=json&filter=upc:${barcode}&field_list=id,issue_number,name,volume,cover_date,cover_price,publisher&limit=5`;
      const res = await fetch(url, { headers: { 'User-Agent': 'ARC2-Comics/1.0' } });
      const data = await res.json();
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ results: data.results || [] })
      };
    }

    if (action === 'variants') {
      const searchUrl = `${BASE_URL}/search/?api_key=${API_KEY}&format=json&query=${encodeURIComponent(series + ' ' + issue)}&resources=issue&field_list=id,issue_number,name,volume,cover_date,cover_price,publisher&limit=10`;
      const res = await fetch(searchUrl, { headers: { 'User-Agent': 'ARC2-Comics/1.0' } });
      const data = await res.json();
      const results = (data.results || []).filter(r =>
        r.issue_number === issue || r.issue_number === String(parseInt(issue))
      );
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ results })
      };
    }

    return {
      statusCode: 400, headers,
      body: JSON.stringify({ error: 'Unknown action' })
    };

  } catch (e) {
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
}