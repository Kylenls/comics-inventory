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
              text: `Analyze this comic book cover photo taken in a lightbox. Return ONLY a JSON object with these exact fields:
{
  "cropTop": 0.05,
  "cropBottom": 0.95,
  "cropLeft": 0.05,
  "cropRight": 0.95,
  "rotation": 0,
  "brightnessAdjust": 0,
  "contrastAdjust": 0,
  "notes": ""
}

Where:
- cropTop/Bottom/Left/Right are 0.0-1.0 fractions of the image to keep (trim dark edges and table)
- rotation is degrees to rotate (-5 to 5) to straighten the comic
- brightnessAdjust is -50 to +50 (positive = brighter)
- contrastAdjust is -50 to +50 (positive = more contrast)
- notes is a brief description of any issues

Focus on: removing black lightbox corners, straightening slightly tilted comics, improving color accuracy. Return ONLY the JSON, no other text.`
            }
          ]
        }]
      })
    });

    const data = await response.json();
    const text = data.content?.[0]?.text || '{}';
    
    let adjustments;
    try {
      adjustments = JSON.parse(text.trim());
    } catch(e) {
      // Default safe crop if parsing fails
      adjustments = {
        cropTop: 0.03,
        cropBottom: 0.97,
        cropLeft: 0.03,
        cropRight: 0.97,
        rotation: 0,
        brightnessAdjust: 5,
        contrastAdjust: 5,
        notes: 'Using default adjustments'
      };
    }

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