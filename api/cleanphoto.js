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
    const { imageBase64, mediaType } = JSON.parse(event.body || '{}');
    if (!imageBase64) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'No image provided' }) };
    }

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-opus-4-5',
        max_tokens: 1024,
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
              text: `This is a comic book cover photo taken in a lightbox. The lightbox has black fabric corners/edges that must be completely removed. Your job is to find the exact boundaries of the comic book cover itself and crop tightly to it.

Look carefully for:
- Where the black lightbox fabric ends and the comic cover begins
- The exact edges of the comic (it may have a white border)
- Any slight tilt that needs correction

Return ONLY a JSON object with no other text:
{
  "cropTop": 0.08,
  "cropBottom": 0.92,
  "cropLeft": 0.08,
  "cropRight": 0.92,
  "rotation": 0,
  "brightnessAdjust": 10,
  "contrastAdjust": 5,
  "notes": ""
}

Rules:
- cropTop/Bottom/Left/Right are 0.0-1.0 fractions indicating what portion of the image to KEEP
- Be AGGRESSIVE with cropping - it is better to crop slightly into the comic than to leave any black fabric visible
- If you see black corners, increase the crop margins until they disappear
- rotation is -5 to +5 degrees to straighten the comic
- brightnessAdjust is -50 to +50 (comics in lightboxes often need +5 to +15)
- contrastAdjust is -50 to +50
- Return ONLY valid JSON, nothing else`
            }
          ]
        }]
      })
    });

    const data = await response.json();
    const text = data.content?.[0]?.text || '{}';
    
    let adjustments;
    try {
      const clean = text.trim().replace(/```json\n?/g, '').replace(/```\n?/g, '');
      adjustments = JSON.parse(clean);
    } catch(e) {
      adjustments = {
        cropTop: 0.08,
        cropBottom: 0.92,
        cropLeft: 0.08,
        cropRight: 0.92,
        rotation: 0,
        brightnessAdjust: 10,
        contrastAdjust: 5,
        notes: 'Using default aggressive crop'
      };
    }

    // Safety clamp values
    adjustments.cropTop = Math.max(0, Math.min(0.4, adjustments.cropTop));
    adjustments.cropBottom = Math.max(0.6, Math.min(1, adjustments.cropBottom));
    adjustments.cropLeft = Math.max(0, Math.min(0.4, adjustments.cropLeft));
    adjustments.cropRight = Math.max(0.6, Math.min(1, adjustments.cropRight));

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, adjustments })
    };

  } catch(e) {
    console.error('cleanphoto error:', e);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};