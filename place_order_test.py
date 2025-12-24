#!/usr/bin/env python3
"""
WEEX API Order Placement Test
Following the exact official documentation format.
"""

import hmac
import hashlib
import base64
import time
import json
import requests

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


def place_order():
    """Place a small test order following the working method."""
    
    # Generate timestamp
    timestamp = str(int(time.time() * 1000))
    
    # Order parameters
    path = "/capi/v2/order/placeOrder"
    method = "POST"
    
    # Get current BTC price first
    ticker_resp = requests.get(f"{BASE_URL}/capi/v2/market/ticker?symbol=cmt_btcusdt")
    ticker = ticker_resp.json()
    current_price = float(ticker.get("last", "87000"))
    
    print(f"Current BTC price: ${current_price}")
    
    # Calculate size for ~15 USDT (max 20 USDT limit)
    target_notional = 15.0  # Target 15 USDT
    size_btc = target_notional / current_price
    size_to_trade = round(size_btc, 4)
    if size_to_trade == 0:
        size_to_trade = 0.0001
    
    notional_value = size_to_trade * current_price
    print(f"Target notional: ${target_notional}")
    print(f"Calculated Size: {size_to_trade} BTC")
    print(f"Actual Notional Value: ~${notional_value:.2f} USDT")
    
    # Use the working format from the example
    order_body = {
        "symbol": "cmt_btcusdt",
        "client_oid": f"test_{int(time.time() * 1000)}",
        "size": str(size_to_trade),  # BTC amount, not contract count!
        "type": "1",           # Open Long
        "order_type": "1",     # Market order
        "match_price": "1",    # Market order
    }
    
    body_str = json.dumps(order_body)
    
    # Generate signature
    signature = generate_signature(timestamp, method, path, body_str)
    
    # Build headers - EXACT format from official docs
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }
    
    url = BASE_URL + path
    
    print("=" * 60)
    print("📤 Placing Order")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Method: {method}")
    print(f"Timestamp: {timestamp}")
    print(f"Headers: {json.dumps({k: v if k != 'ACCESS-SIGN' else v[:20]+'...' for k, v in headers.items()}, indent=2)}")
    print(f"Body: {json.dumps(order_body, indent=2)}")
    print()
    
    # Make request
    try:
        response = requests.post(url, headers=headers, data=body_str, timeout=30)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"error": str(e)}


def get_account_info():
    """Get account info to understand margin."""
    timestamp = str(int(time.time() * 1000))
    path = "/capi/v2/account/getAccounts"
    method = "GET"
    
    signature = generate_signature(timestamp, method, path, "")
    
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }
    
    url = BASE_URL + path
    
    print("=" * 60)
    print("📊 Getting Account Info")
    print("=" * 60)
    
    response = requests.get(url, headers=headers, timeout=30)
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(result, indent=2)}")
    return result


def get_current_orders():
    """Check for any existing open orders."""
    timestamp = str(int(time.time() * 1000))
    path = "/capi/v2/order/current"
    method = "GET"
    
    signature = generate_signature(timestamp, method, path, "")
    
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }
    
    url = BASE_URL + path
    
    print("=" * 60)
    print("📋 Checking Current Open Orders")
    print("=" * 60)
    
    response = requests.get(url, headers=headers, timeout=30)
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(result, indent=2)}")
    return result


def get_positions():
    """Get current positions."""
    timestamp = str(int(time.time() * 1000))
    path = "/capi/v2/account/position/allPosition"
    method = "GET"
    
    signature = generate_signature(timestamp, method, path, "")
    
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }
    
    url = BASE_URL + path
    
    print("=" * 60)
    print("📊 Checking Current Positions")
    print("=" * 60)
    
    response = requests.get(url, headers=headers, timeout=30)
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(result, indent=2)}")
    return result


def close_position():
    """Try to close all positions to free margin."""
    timestamp = str(int(time.time() * 1000))
    path = "/capi/v2/order/closePositions"
    method = "POST"
    
    body = {
        "symbol": "cmt_btcusdt"
    }
    body_str = json.dumps(body)
    
    signature = generate_signature(timestamp, method, path, body_str)
    
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }
    
    url = BASE_URL + path
    
    print("=" * 60)
    print("🔒 Closing All Positions")
    print("=" * 60)
    
    response = requests.post(url, headers=headers, data=body_str, timeout=30)
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(result, indent=2)}")
    return result


def get_assets():
    """Get account assets."""
    timestamp = str(int(time.time() * 1000))
    path = "/capi/v2/account/assets"
    method = "GET"
    
    signature = generate_signature(timestamp, method, path, "")
    
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }
    
    url = BASE_URL + path
    
    print("=" * 60)
    print("💰 Checking Account Assets")
    print("=" * 60)
    
    response = requests.get(url, headers=headers, timeout=30)
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(result, indent=2)}")
    return result


if __name__ == "__main__":
    print("\n🚀 WEEX API Order Test\n")
    
    # Check current assets
    get_assets()
    print("\n")
    
    # Check current orders
    get_current_orders()
    print("\n")
    
    # Check positions
    get_positions()
    print("\n")
    
    # Wait a moment for settlement
    print("⏳ Waiting 2 seconds for settlement...")
    time.sleep(2)
    print("\n")
    
    # Check assets again
    get_assets()
    print("\n")
    
    # Then try to place order
    place_order()

