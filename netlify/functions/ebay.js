const https = require('https');
const xml2js = require('xml2js');

const EBAY_USER_TOKEN = process.env.EBAY_USER_TOKEN;
const EBAY_APP_ID = process.env.EBAY_APP_ID;
const EBAY_DEV_ID = process.env.EBAY_DEV_ID;
const EBAY_CERT_ID = process.env.EBAY_CERT_ID;

// eBay Trading API endpoint (production)
const EBAY_API_URL = 'https://api.ebay.com/ws/api.dll';

function makeEbayRequest(callName, xmlBody) {
  return new Promise((resolve, reject) => {
    const headers = {
      'X-EBAY-API-SITEID': '0',
      'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
      'X-EBAY-API-CALL-NAME': callName,
      'X-EBAY-API-APP-NAME': EBAY_APP_ID,
      'X-EBAY-API-DEV-NAME': EBAY_DEV_ID,
      'X-EBAY-API-CERT-NAME': EBAY_CERT_ID,
      'Content-Type': 'text/xml',
      'Content-Length': Buffer.byteLength(xmlBody)
    };

    const options = {
      hostname: 'api.ebay.com',
      path: '/ws/api.dll',
      method: 'POST',
      headers
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
    req.write(xmlBody);
    req.end();
  });
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
    const body = JSON.parse(event.body || '{}');
    const { action } = body;

    if (action === 'create_listing') {
      const {
        title, description, price, category_id,
        condition_id, quantity, pictures,
        item_specifics, shipping_profile_id,
        payment_profile_id, return_profile_id
      } = body;

      // Build item specifics XML
      const specificsList = (item_specifics || []).map(s =>
        `<NameValueList><Name>${s.name}</Name><Value>${s.value}</Value></NameValueList>`
      ).join('');

      // Build pictures XML
      const picturesList = (pictures || []).map(url =>
        `<PictureURL>${url}</PictureURL>`
      ).join('');

      const xml = `<?xml version="1.0" encoding="utf-8"?>
<AddFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>${EBAY_USER_TOKEN}</eBayAuthToken>
  </RequesterCredentials>
  <Item>
    <Title>${title}</Title>
    <Description><![CDATA[${description}]]></Description>
    <PrimaryCategory><CategoryID>${category_id || '259104'}</CategoryID></PrimaryCategory>
    <StartPrice>${price}</StartPrice>
    <ConditionID>${condition_id || '1000'}</ConditionID>
    <Country>US</Country>
    <Currency>USD</Currency>
    <DispatchTimeMax>1</DispatchTimeMax>
    <ListingDuration>GTC</ListingDuration>
    <ListingType>FixedPriceItem</ListingType>
    <Quantity>${quantity || 1}</Quantity>
    <ShipToLocations>US</ShipToLocations>
    ${picturesList ? '<PictureDetails>' + picturesList + '</PictureDetails>' : ''}
    ${specificsList ? '<ItemSpecifics>' + specificsList + '</ItemSpecifics>' : ''}
    <ShippingDetails>
      <ShippingType>Flat</ShippingType>
      <ShippingServiceOptions>
        <ShippingServicePriority>1</ShippingServicePriority>
        <ShippingService>USPSMedia</ShippingService>
        <ShippingServiceCost>0.00</ShippingServiceCost>
        <FreeShipping>true</FreeShipping>
      </ShippingServiceOptions>
    </ShippingDetails>
    <ReturnPolicy>
      <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
      <RefundOption>MoneyBack</RefundOption>
      <ReturnsWithinOption>Days_30</ReturnsWithinOption>
      <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
    </ReturnPolicy>
  </Item>
</AddFixedPriceItemRequest>`;

      const response = await makeEbayRequest('AddFixedPriceItem', xml);
      const parsed = await xml2js.parseStringPromise(response, { explicitArray: false });
      const result = parsed.AddFixedPriceItemResponse;

      if (result.Ack === 'Success' || result.Ack === 'Warning') {
        return {
          statusCode: 200, headers,
          body: JSON.stringify({
            success: true,
            itemId: result.ItemID,
            fees: result.Fees,
            ack: result.Ack
          })
        };
      } else {
        const errors = result.Errors;
        return {
          statusCode: 400, headers,
          body: JSON.stringify({
            success: false,
            errors: Array.isArray(errors) ? errors : [errors]
          })
        };
      }
    }

    if (action === 'end_listing') {
      const { item_id, reason } = body;
      const xml = `<?xml version="1.0" encoding="utf-8"?>
<EndFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>${EBAY_USER_TOKEN}</eBayAuthToken>
  </RequesterCredentials>
  <ItemID>${item_id}</ItemID>
  <EndingReason>${reason || 'NotAvailable'}</EndingReason>
</EndFixedPriceItemRequest>`;

      const response = await makeEbayRequest('EndFixedPriceItem', xml);
      const parsed = await xml2js.parseStringPromise(response, { explicitArray: false });
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true, response: parsed })
      };
    }

    if (action === 'revise_price') {
      const { item_id, price } = body;
      const xml = `<?xml version="1.0" encoding="utf-8"?>
<ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>${EBAY_USER_TOKEN}</eBayAuthToken>
  </RequesterCredentials>
  <Item>
    <ItemID>${item_id}</ItemID>
    <StartPrice>${price}</StartPrice>
  </Item>
</ReviseFixedPriceItemRequest>`;

      const response = await makeEbayRequest('ReviseFixedPriceItem', xml);
      const parsed = await xml2js.parseStringPromise(response, { explicitArray: false });
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true, response: parsed })
      };
    }

    if (action === 'get_listing') {
      const { item_id } = body;
      const xml = `<?xml version="1.0" encoding="utf-8"?>
<GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>${EBAY_USER_TOKEN}</eBayAuthToken>
  </RequesterCredentials>
  <ItemID>${item_id}</ItemID>
</GetItemRequest>`;

      const response = await makeEbayRequest('GetItem', xml);
      const parsed = await xml2js.parseStringPromise(response, { explicitArray: false });
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ success: true, item: parsed.GetItemResponse?.Item })
      };
    }

    return {
      statusCode: 400, headers,
      body: JSON.stringify({ error: 'Unknown action: ' + action })
    };

  } catch(e) {
    console.error('ebay function error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: e.message })
    };
  }
};