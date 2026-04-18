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
    const body = JSON.parse(event.body || '{}');
    const { action, id, fields, table, formula, sortField, sortDir, maxRecords, offset } = body;
    const useTable = table || TABLE;

    if (action === 'list') {
      const params = {};
      if (sortField) params.sort = [{ field: sortField, direction: sortDir || 'asc' }];
      if (maxRecords) params.maxRecords = maxRecords;
      if (formula) params.filterByFormula = formula;
      if (offset) params.offset = offset;

      const records = [];
      let returnOffset = null;

      await new Promise((resolve, reject) => {
        base(useTable).select({ ...params, pageSize: 100 }).eachPage(
          (pageRecords, fetchNextPage) => {
            pageRecords.forEach(r => records.push({ id: r.id, fields: r.fields }));
            if (offset || maxRecords) {
              resolve();
            } else {
              fetchNextPage();
            }
          },
          (err) => {
            if (err) reject(err);
            else resolve();
          }
        );
      });

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ records, offset: null })
      };
    }

    if (action === 'search') {
      const params = { pageSize: 100 };
      if (formula) params.filterByFormula = formula;
      if (sortField) params.sort = [{ field: sortField, direction: sortDir || 'asc' }];
      if (maxRecords) params.maxRecords = maxRecords;
      if (offset) params.offset = offset;

      const records = [];
      let returnOffset = null;

      await new Promise((resolve, reject) => {
        base(useTable).select(params).eachPage(
          (pageRecords, fetchNextPage) => {
            pageRecords.forEach(r => records.push({ id: r.id, fields: r.fields }));
            if (maxRecords && records.length >= maxRecords) {
              resolve();
            } else {
              fetchNextPage();
            }
          },
          (err) => {
            if (err) reject(err);
            else resolve();
          }
        );
      });

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ records, offset: returnOffset })
      };
    }

    if (action === 'create') {
      const record = await base(useTable).create(fields);
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ id: record.id, fields: record.fields })
      };
    }

    if (action === 'update') {
      const record = await base(useTable).update(id, fields);
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ id: record.id, fields: record.fields })
      };
    }

    if (action === 'delete') {
      await base(useTable).destroy(id);
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ deleted: true, id })
      };
    }

    if (action === 'upsert') {
      const sku = fields['SKU'];
      if (!sku) {
        const record = await base(useTable).create(fields);
        return {
          statusCode: 200, headers,
          body: JSON.stringify({ id: record.id, fields: record.fields })
        };
      }

      const existing = await base(useTable).select({
        filterByFormula: `{SKU}="${sku}"`,
        maxRecords: 1
      }).firstPage();

      if (existing.length > 0) {
        return {
          statusCode: 200, headers,
          body: JSON.stringify({ id: existing[0].id, fields: existing[0].fields, _action: 'skipped' })
        };
      }

      const record = await base(useTable).create(fields);
      return {
        statusCode: 200, headers,
        body: JSON.stringify({ id: record.id, fields: record.fields, _action: 'created' })
      };
    }

    return {
      statusCode: 400, headers,
      body: JSON.stringify({ error: 'Unknown action: ' + action })
    };

  } catch (e) {
    console.error('Airtable error:', e);
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ error: { message: e.message } })
    };
  }
};