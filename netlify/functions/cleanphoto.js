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
    const { imageBase64, mediaType } = body;
    
    if (!imageBase64) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'No image provided' }) };
    }

    console.log('cleanphoto: image size', imageBase64.length, 'chars');
    console.log('cleanphoto: ANTHROPIC_KEY present:', !!process.env.ANTHROPIC_KEY);

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 512,
        messages: [{
          role: 'user',
          content: [
            {
              type: 'image',
              source: {
                type: 'base64',
                media_type: mediaType || 'image/jpeg',
                data: imageBase64
              }
            },
            {
              type: 'text',
              text: `Look at this comic book photo taken in a lightbox. Return ONLY this JSON with crop values to remove black edges:
{"cropTop":0.05,"cropBottom":0.95,"cropLeft":0.05,"cropRight":0.95,"rotation":0,"brightnessAdjust":10,"contrastAdjust":5,"notes":""}
Adjust the crop values to tightly frame the comic cover, removing black lightbox corners. Return ONLY valid JSON.`
            }
          ]
        }]
      })
    });

    console.log('cleanphoto: API status', response.status);
    const data = await response.json();
    console.log('cleanphoto: API response', JSON.stringify(data).slice(0, 200));

    if (data.error) {
      return { statusCode: 500, headers, body: JSON.stringify({ error: data.error.message }) };
    }

    const text = data.content?.[0]?.text || '{}';
    console.log('cleanphoto: text response', text);
    
    let adjustments;
    try {
      const clean = text.trim().replace(/```json\n?/g, '').replace(/```\n?/g, '');
      adjustments = JSON.parse(clean);
    } catch(e) {
      adjustments = {
        cropTop: 0.06, cropBottom: 0.94, cropLeft: 0.06, cropRight: 0.94,
        rotation: 0, brightnessAdjust: 10, contrastAdjust: 5, notes: 'default'
      };
    }

    adjustments.cropTop = Math.max(0, Math.min(0.4, adjustments.cropTop || 0.06));
    adjustments.cropBottom = Math.max(0.6, Math.min(1, adjustments.cropBottom || 0.94));
    adjustments.cropLeft = Math.max(0, Math.min(0.4, adjustments.cropLeft || 0.06));
    adjustments.cropRight = Math.max(0.6, Math.min(1, adjustments.cropRight || 0.94));

    return { statusCode: 200, headers, body: JSON.stringify({ success: true, adjustments }) };

  } catch(e) {
    console.error('cleanphoto error:', e.message, e.stack);
    return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
  }
};