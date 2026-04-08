import asyncio
import httpx
import json

async def test_end_to_end_scan():
    print("====================================")
    print("AppGuardAi API E2E Testing Sequence")
    print("====================================")
    
    base_url = "http://127.0.0.1:8000/api/v1"
    
    # Simulate Payload from Mobile App (Full Device Scan)
    payload = {
        "apps": [
            {"app_name": "Google Chrome", "package_name": "com.android.chrome.test1", "version_name": "120", "hash_sha256": "fakehash_safe_chrome", "is_system_app": True},
            {"app_name": "Shady Flashlight App", "package_name": "com.flashlight.malware.hack.test1", "version_name": "1.0", "hash_sha256": "fakehash_malware", "is_system_app": False},
            {"app_name": "Calculator", "package_name": "com.android.calculator2.test1", "version_name": "8.0", "hash_sha256": "", "is_system_app": True}
        ]
    }
    
    print("\n[+] 1. Testing POST /api/v1/scan ...")
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{base_url}/scan", json=payload, timeout=20.0)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("- Total Scanned:", data.get('total_scanned'))
            print("- Safe Apps Count:", data.get('safe_apps_count'))
            print("- Risky Apps Count:", data.get('risky_apps_count'))
            print("- Risky Apps payload sample:", json.dumps(data.get('risky_apps', []), indent=2))
        else:
            print("- Failed! Output:", res.text)
            
    print("\n[+] 2. Testing POST /api/v1/whitelist ...")
    whitelist_payload = {
        "package_name": "com.flashlight.malware.hack"
    }
    async with httpx.AsyncClient() as client:
        res2 = await client.post(f"{base_url}/whitelist", json=whitelist_payload, timeout=10.0)
        print(f"Status Code: {res2.status_code}")
        print("Response:", res2.json() if res2.status_code == 200 else res2.text)

    print("\n[+] End-to-End sequence complete. Compare this sequence to your Supabase Database entries!")

if __name__ == "__main__":
    asyncio.run(test_end_to_end_scan())
