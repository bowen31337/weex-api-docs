#!/usr/bin/env python3
"""
WEEX API Test Script
Tests authenticated API endpoints with proper HMAC-SHA256 signature generation.
"""

import hmac
import hashlib
import base64
import time
import json
import requests
from typing import Optional

# API Credentials - Set these environment variables or replace with your own
import os
API_KEY = os.environ.get("WEEX_API_KEY", "your_api_key")
API_SECRET = os.environ.get("WEEX_API_SECRET", "your_api_secret")
PASSPHRASE = os.environ.get("WEEX_PASSPHRASE", "your_passphrase")
BASE_URL = "https://api-contract.weex.com"


def generate_signature(timestamp: str, method: str, path: str, body: str = "") -> str:
    """Generate HMAC-SHA256 signature for WEEX API."""
    message = timestamp + method.upper() + path + body
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    return signature


def make_request(method: str, path: str, params: Optional[dict] = None, body: Optional[dict] = None) -> dict:
    """Make an authenticated request to WEEX API."""
    timestamp = str(int(time.time() * 1000))
    
    # Build URL with query params
    url = BASE_URL + path
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url += "?" + query_string
    
    # Prepare body
    body_str = json.dumps(body) if body else ""
    
    # Generate signature (path only, not full URL with params for GET)
    sign_path = path
    if method.upper() == "GET" and params:
        sign_path = path + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    signature = generate_signature(timestamp, method, sign_path, body_str if method.upper() != "GET" else "")
    
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "locale": "en-US"
    }
    
    print(f"\n{'='*60}")
    print(f"🔹 {method.upper()} {path}")
    print(f"{'='*60}")
    print(f"Timestamp: {timestamp}")
    print(f"URL: {url}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, data=body_str, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"error": str(e)}


def test_server_time():
    """Test server time endpoint (no auth required)."""
    print("\n" + "="*60)
    print("📊 Testing Server Time (No Auth)")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/capi/v2/market/time")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


def test_account_list():
    """Test getting account list."""
    return make_request("GET", "/capi/v2/account/getAccounts")


def test_account_assets():
    """Test getting account assets."""
    return make_request("GET", "/capi/v2/account/assets")


def test_single_account():
    """Test getting single account info."""
    return make_request("GET", "/capi/v2/account/getAccount", {"symbol": "cmt_btcusdt"})


def test_all_positions():
    """Test getting all positions."""
    return make_request("GET", "/capi/v2/account/position/allPosition")


def test_current_orders():
    """Test getting current open orders."""
    return make_request("GET", "/capi/v2/order/current")


def test_btc_ticker():
    """Get BTC ticker info."""
    print("\n" + "="*60)
    print("📊 BTC/USDT Ticker (No Auth)")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/capi/v2/market/ticker", params={"symbol": "cmt_btcusdt"})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


def test_contracts_info():
    """Get contract info to understand min order sizes."""
    print("\n" + "="*60)
    print("📊 Contract Info (No Auth)")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/capi/v2/market/contracts", params={"symbol": "cmt_btcusdt"})
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return result


def main():
    """Run all tests."""
    print("\n" + "🚀" * 30)
    print("   WEEX API Test Suite")
    print("🚀" * 30)
    
    # Test public endpoints
    test_server_time()
    test_btc_ticker()
    test_contracts_info()
    
    # Test authenticated endpoints
    print("\n\n" + "🔐" * 30)
    print("   AUTHENTICATED ENDPOINTS")
    print("🔐" * 30)
    
    test_account_list()
    test_account_assets()
    test_single_account()
    test_all_positions()
    test_current_orders()
    
    print("\n\n" + "✅" * 30)
    print("   Test Suite Complete")
    print("✅" * 30)


if __name__ == "__main__":
    main()

