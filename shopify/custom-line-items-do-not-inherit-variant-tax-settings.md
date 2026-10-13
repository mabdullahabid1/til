# Shopify Custom Line Items Do Not Inherit Variant Tax Settings

A Shopify custom line item is not linked to a catalog variant. Without a `variant_id`, it cannot inherit that variant's tax configuration and may be treated as taxable even when the catalog item is exempt.

For a catalog-backed item, send the variant ID:

```json
{
  "line_items": [
    {
      "variant_id": 123456789,
      "quantity": 1
    }
  ]
}
```

For a deliberately custom line, set its tax behavior explicitly instead of assuming Shopify can infer it from a title, SKU, or price.

After creation, inspect the resulting line item and order tax lines. A `201` response proves the request was accepted, not that the stored tax behavior matches the catalog item you meant to represent.
