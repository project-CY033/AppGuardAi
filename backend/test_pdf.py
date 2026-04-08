import httpx
import sys

def test_pdf_scan():
    # create a dummy pdf
    with open("dummy.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF")

    try:
        with open("dummy.pdf", "rb") as f:
            files = {'file': ("dummy.pdf", f, "application/pdf")}
            res = httpx.post("http://127.0.0.1:8000/api/v1/scan/pdf", files=files, timeout=30)
            print(f"Status Code: {res.status_code}")
            print(res.text)
            
            if res.status_code == 200:
                body = res.json()
                file_id = body.get("id")
                if file_id:
                    print(f"File ID: {file_id}, hitting delete...")
                    d_res = httpx.delete(f"http://127.0.0.1:8000/api/v1/scan/pdf/{file_id}", timeout=10)
                    print(f"Delete Status: {d_res.status_code}")
                    print(d_res.text)
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_pdf_scan()
