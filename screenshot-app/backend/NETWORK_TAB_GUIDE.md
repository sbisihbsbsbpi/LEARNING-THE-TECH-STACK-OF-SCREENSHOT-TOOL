# 🌐 Network Tab - API Extraction & Documentation Guide

## Overview

The Network tab provides powerful tools for extracting, validating, and documenting API responses. It auto-generates metadata schemas, extracts fields, validates responses, and compares data across environments.

---

## Features

### 1. 🔍 Generate Metadata
Auto-generate field mappings from any API response JSON.

**Use Case:** You have an API response and want to create a metadata schema automatically.

**Example Input:**
```json
{
  "data": {
    "dealerName": "ABC Motors",
    "id": "123",
    "dealerAddress": [
      {
        "city": "New York",
        "state": "NY"
      }
    ]
  }
}
```

**Generated Output:**
```json
{
  "dealerName": {
    "api_path": "data.dealerName",
    "type": "string",
    "display_name": "Dealer Name"
  },
  "id": {
    "api_path": "data.id",
    "type": "string",
    "display_name": "Id"
  },
  "dealerAddress[].city": {
    "api_path": "data.dealerAddress[*].city",
    "type": "string",
    "display_name": "Dealer Address City"
  },
  "dealerAddress[].state": {
    "api_path": "data.dealerAddress[*].state",
    "type": "string",
    "display_name": "Dealer Address State"
  }
}
```

---

### 2. 📦 Extract Fields
Extract specific fields from an API response using metadata mappings.

**Use Case:** You have metadata and want to extract actual values from a response.

**Example:**
- **API Response:** Same as above
- **Field Mappings:** Generated metadata from step 1
- **Result:** Extracted values with display names and types

---

### 3. ✅ Validate Response
Validate an API response against expected metadata schema.

**Use Case:** Check if an API response has all required fields with correct types.

**Example:**
- **API Response:** Your actual API response
- **Expected Metadata:** Your metadata schema
- **Result:** Validation report showing missing fields and type mismatches

**Validation Report:**
```json
{
  "total_fields": 10,
  "fields_found": 8,
  "fields_missing": 2,
  "type_mismatches": 1,
  "validation_passed": false,
  "missing_fields": [
    {
      "field_id": "dealerEmail",
      "api_path": "data.dealerEmail",
      "expected_type": "string"
    }
  ],
  "type_mismatch_details": [
    {
      "field_id": "dealerId",
      "expected_type": "string",
      "actual_type": "number"
    }
  ]
}
```

---

### 4. 📊 Compare Environments
Compare the same API response across dev, staging, and prod environments.

**Use Case:** Identify differences in API responses between environments.

**Example:**
- **Dev Extraction:** API response from dev environment
- **Staging Extraction:** API response from staging environment
- **Prod Extraction:** API response from prod environment
- **Result:** Comparison report showing which fields differ

**Comparison Report:**
```json
{
  "environments": ["dev", "staging", "prod"],
  "summary": {
    "total_fields": 20,
    "identical_fields": 18,
    "fields_with_differences": 2
  },
  "differences": [
    {
      "field_id": "apiVersion",
      "values": {
        "dev": "2.0.0",
        "staging": "2.0.1",
        "prod": "1.9.5"
      }
    }
  ]
}
```

---

## API Endpoints

### POST `/api/network/generate-metadata`
Generate metadata from API response.

**Request:**
```json
{
  "data": { ... API response ... },
  "prefix": "data",
  "max_depth": 10
}
```

### POST `/api/network/extract-fields`
Extract fields from API response.

**Request:**
```json
{
  "response_data": { ... API response ... },
  "field_mappings": { ... metadata ... }
}
```

### POST `/api/network/validate`
Validate API response.

**Request:**
```json
{
  "response_data": { ... API response ... },
  "metadata": { ... expected metadata ... }
}
```

### POST `/api/network/compare-environments`
Compare across environments.

**Request:**
```json
{
  "extractions": {
    "dev": { ... extraction result ... },
    "staging": { ... extraction result ... },
    "prod": { ... extraction result ... }
  }
}
```

---

## Tips

1. **Start with Generate Metadata** - Always generate metadata first from a sample API response
2. **Copy to Clipboard** - Use the copy button to save generated metadata
3. **Validate Before Comparing** - Validate each environment's response before comparing
4. **Use JSON Path** - Metadata uses JSON path syntax (e.g., `data[*].id` for arrays)

---

## Future Enhancements

- [ ] Live API interception during screenshot capture
- [ ] Save metadata schemas to files
- [ ] Export documentation as Markdown/HTML
- [ ] Batch validation across multiple APIs
- [ ] Visual diff viewer for environment comparisons

