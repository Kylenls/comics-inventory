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
    const { action, id, fields, table, formula, sortField, sortDir, maxRecords, offset, sessionCount } = body;
    const useTable = table || TABLE;

    if (action === 'list') {
      const params = {};
      if (sortField) params.sort = [{ field: sortField, direction: sortDir || 'asc' }];
      if (maxRecords) params.maxRecords = maxRecords;
      if (formula) params.filterByFormula = formula;
      if (offset) params.offset = offset;

      const records = [];

      await new Promise((resolve, reject) => {
        base(useTable).select({ ...params, pageSize: 100 }).eachPage(
          (pageRecords, fetchNextPage) => {
            pageRecords.forEach(r => records.push({ id: r.id, fields: r.fields }));
            if (offset || maxRecords) resolve();
            else fetchNextPage();
          },
          (err) => { if (err) reject(err); else resolve(); }
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

      await new Promise((resolve, reject) => {
        base(useTable).select(params).eachPage(
          (pageRecords, fetchNextPage) => {
            pageRecords.forEach(r => records.push({ id: r.id, fields: r.fields }));
            if (maxRecords && records.length >= maxRecords) resolve();
            else fetchNextPage();
          },
          (err) => { if (err) reject(err); else resolve(); }
        );
      });

      return {
        statusCode: 200, headers,
        body: JSON.stringify({ records, offset: null })
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
      const series = (fields['Series'] || '').trim();
      const issue = (fields['Issue'] || '').trim();
      const variant = (fields['Variant'] || '').trim();
      const currentSessionCount = sessionCount || 0;

      if (!series) {
        const record = await base(useTable).create(fields);
        return {
          statusCode: 200, headers,
          body: JSON.stringify({ id: record.id, fields: record.fields, _action: 'created' })
        };
      }

      const escapedSeries = series.replace(/'/g, "\\'");
      const escapedIssue = issue.replace(/'/g, "\\'");
      const escapedVariant = variant.replace(/'/g, "\\'");

      let filterFormula;
      if (variant) {
        filterFormula = `AND({Series}='${escapedSeries}',{Issue}='${escapedIssue}',{Variant}='${escapedVariant}',{Status}!='Sold')`;
      } else {
        filterFormula = `AND({Series}='${escapedSeries}',{Issue}='${escapedIssue}',OR({Variant}='',{Variant}=BLANK()),{Status}!='Sold')`;
      }

      const existing = await base(useTable).select({
        filterByFormula: filterFormula,
        fields: ['SKU', 'Status']
      }).firstPage();

      // If we already have more records than sessionCount allows, skip
      if (existing.length > currentSessionCount) {
        return {
          statusCode: 200, headers,
          body: JSON.stringify({
            id: existing[0].id,
            fields: existing[0].fields,
            _action: 'skipped'
          })
        };
      }

      // Create new record
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