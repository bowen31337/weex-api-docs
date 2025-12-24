# WEEX Futures Trading API Changelog

All notable changes to the WEEX Futures Trading API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this API adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2024-12-24

### Added
- **AI Integration Endpoint**: New `/capi/v2/order/uploadAiLog` endpoint for AI-powered trading verification
- **Comprehensive Error Responses**: All endpoints now document 400, 401, 403, 429, and 500 error responses
- **Interactive Documentation**: Automatic signature generation in Swagger UI
- **Getting Started Guide**: Step-by-step quick start tutorial
- **Code Examples**: Python and JavaScript authentication examples
- **Glossary**: Trading terminology definitions
- **FAQ Section**: Answers to common integration questions
- **Rate Limiting Documentation**: Detailed rate limit tables and handling guidance

### Changed
- Updated OpenAPI specification to version 3.1.0
- Enhanced endpoint descriptions with use cases and workflow guidance
- Improved parameter documentation with realistic examples
- Added example responses for all major endpoints

### Fixed
- Resolved YAML parsing issues with special characters in descriptions
- Fixed nullable property syntax for OpenAPI 3.1 compliance
- Removed trailing slash from server URL

---

## [1.5.0] - 2024-09-15

### Added
- **TP/SL Orders**: Take-profit and stop-loss order endpoints
  - `POST /capi/v2/order/placeTpSlOrder`
  - `POST /capi/v2/order/modifyTpSlOrder`
- **Trigger Orders**: Plan/conditional order support
  - `POST /capi/v2/order/plan_order`
  - `POST /capi/v2/order/cancel_plan`
  - `GET /capi/v2/order/currentPlan`
  - `GET /capi/v2/order/historyPlan`

### Changed
- Increased maximum leverage to 125x for major pairs

---

## [1.4.0] - 2024-06-01

### Added
- **Batch Operations**
  - `POST /capi/v2/order/cancelAllOrders`
  - `POST /capi/v2/order/closePositions`
- **Position Management**
  - `GET /capi/v2/account/position/allPosition`
  - `GET /capi/v2/account/position/singlePosition`

### Changed
- Improved order fill response with more details

---

## [1.3.0] - 2024-03-15

### Added
- **Funding Rate Endpoints**
  - `GET /capi/v2/market/funding_time`
  - `GET /capi/v2/market/getHistoryFundRate`
  - `GET /capi/v2/market/currentFundRate`
- **Open Interest**: `GET /capi/v2/market/open_interest`

### Changed
- Enhanced ticker data with mark and index prices

---

## [1.2.0] - 2024-01-10

### Added
- **Account Bill History**: `POST /capi/v2/account/bills`
- **Margin Adjustment**: `POST /capi/v2/account/adjustMargin`
- **Auto Margin Top-up**: `POST /capi/v2/account/modifyAutoAppendMargin`

### Changed
- Added margin mode support to order placement

---

## [1.1.0] - 2023-10-01

### Added
- **Order History**: `GET /capi/v2/order/history`
- **Fill Details**: `GET /capi/v2/order/fills`
- Candlestick data with multiple granularities

### Fixed
- Improved timestamp precision for order matching

---

## [1.0.0] - 2023-07-01

### Added
- Initial API release
- **Market Data Endpoints**
  - Server time
  - Contracts information
  - Order book depth
  - Ticker data
  - Trade history
  - Candlestick data
- **Account Endpoints**
  - Account information
  - Asset balances
  - Leverage settings
- **Order Endpoints**
  - Place order
  - Cancel order
  - Order details
  - Current orders

---

## Migration Guides

### Migrating from v1.x to v2.0

#### Breaking Changes
None. Version 2.0 is backward compatible with 1.x.

#### Recommended Updates

1. **Update Error Handling**
   - Add handlers for new documented error codes
   - Implement retry logic for 429 (rate limit) errors

2. **Use New Features**
   - Leverage the AI log endpoint for automated trading verification
   - Utilize TP/SL orders for risk management

3. **Update Documentation References**
   - Use the new interactive documentation
   - Refer to the glossary for trading terminology

---

## Deprecation Notices

Currently, no endpoints are deprecated. All v1.x endpoints remain fully functional.

---

## Support

For API issues or questions:
- **Support Center**: [weex.com/help](https://www.weex.com/help)
- **Official Website**: [weex.com](https://www.weex.com)

