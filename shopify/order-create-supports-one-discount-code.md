# Shopify Order Creation Supports One Discount Code

Shopify can accept an order-creation request containing multiple discount-code entries while applying only the first one. A successful response therefore does not prove every requested discount survived.

The Admin GraphQL API models the order-level discount as a single `OrderCreateDiscountCodeInput`:

```graphql
discountCode: {
  itemPercentageDiscountCode: {
    code: "COMBINED_DISCOUNT"
    percentage: 12
  }
}
```

When creating an order directly:

1. Send one combined order-level discount.
2. Inspect the returned `discountApplications` and totals.
3. Treat the persisted business result, not the HTTP status, as the success condition.

If the workflow requires multiple independent discounts, evaluate a different Shopify order flow and verify it with a real staging replay before relying on it.
