#!/usr/bin/env python3
"""
Test connection to Nano Banana Pro API and verify credentials.

Usage:
    python test_connection.py --api-key YOUR_KEY
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("Error: requests library not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


def test_api_connection(api_key: str, model: str = "gemini-3-pro-image-preview") -> dict:
    """
    Test API connection with a simple request.

    Args:
        api_key: Gemini API key
        model: Model to test

    Returns:
        Dictionary with test results
    """
    results = {
        "api_key_present": bool(api_key),
        "api_key_format": "valid" if api_key and api_key.startswith("AIza") else "invalid",
        "connection_test": "not_run",
        "model_available": False,
        "error": None
    }

    if not api_key:
        results["error"] = "No API key provided"
        return results

    # Test simple generation request
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    # Simple test prompt
    payload = {
        "contents": [{
            "parts": [{"text": "Generate a small test image: red circle"}]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "maxOutputTokens": 512,
            "imageConfig": {
                "aspectRatio": "1:1"
            }
        }
    }

    try:
        print("🔍 Testing API connection...")
        print(f"   Endpoint: {endpoint}")
        print(f"   Model: {model}")
        print()

        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )

        results["connection_test"] = "completed"
        results["status_code"] = response.status_code

        if response.status_code == 200:
            results["model_available"] = True
            response_data = response.json()

            # Check if image was generated
            candidates = response_data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                has_image = any("inlineData" in part for part in parts)
                results["image_generated"] = has_image

            results["success"] = True

        else:
            results["success"] = False
            try:
                error_data = response.json()
                results["error"] = error_data.get("error", {}).get("message", response.text)
            except:
                results["error"] = response.text

    except requests.exceptions.Timeout:
        results["connection_test"] = "timeout"
        results["error"] = "Request timed out after 30 seconds"

    except requests.exceptions.ConnectionError as e:
        results["connection_test"] = "connection_error"
        results["error"] = f"Connection error: {e}"

    except Exception as e:
        results["connection_test"] = "error"
        results["error"] = str(e)

    return results


def print_results(results: dict):
    """Print test results in a readable format."""

    print("=" * 60)
    print("🧪 API CONNECTION TEST RESULTS")
    print("=" * 60)
    print()

    # API Key Status
    print("📋 API Key Status:")
    print(f"   Present: {'✓' if results['api_key_present'] else '✗'}")
    print(f"   Format: {results['api_key_format']}")
    print()

    # Connection Test
    print("🌐 Connection Test:")
    status = results['connection_test']
    status_icon = "✓" if status == "completed" else "✗"
    print(f"   Status: {status_icon} {status}")

    if "status_code" in results:
        code_icon = "✓" if results.get("success") else "✗"
        print(f"   HTTP Code: {code_icon} {results['status_code']}")

    print()

    # Model Availability
    print("🤖 Model Availability:")
    model_icon = "✓" if results.get("model_available") else "✗"
    print(f"   Available: {model_icon} {results.get('model_available', False)}")

    if results.get("image_generated"):
        print(f"   Image Generation: ✓ Working")

    print()

    # Error Details
    if results.get("error"):
        print("❌ Error Details:")
        print(f"   {results['error']}")
        print()

    # Summary
    print("=" * 60)
    if results.get("success"):
        print("✅ SUCCESS: API connection is working correctly!")
        print()
        print("You can now use Nano Banana Pro for image generation.")
    else:
        print("❌ FAILED: API connection test failed")
        print()
        print("Troubleshooting tips:")
        print("  1. Verify your API key is correct")
        print("  2. Check if billing is enabled in Google AI Studio")
        print("  3. Ensure the model is available in your region")
        print("  4. Check network connectivity")
        print("  5. Review error message above for specific issues")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Test Nano Banana Pro API connection",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--model", default="gemini-3-pro-image-preview",
                       help="Model to test (default: gemini-3-pro-image-preview)")
    parser.add_argument("--json", action="store_true",
                       help="Output results as JSON")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Error: API key required. Use --api-key or set GEMINI_API_KEY environment variable",
              file=sys.stderr)
        sys.exit(1)

    # Run test
    results = test_api_connection(api_key, args.model)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results)

    # Exit with appropriate code
    sys.exit(0 if results.get("success") else 1)


if __name__ == "__main__":
    main()
