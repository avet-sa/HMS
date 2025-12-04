import urllib.request
import urllib.error


def test_options_request():
    url = "http://127.0.0.1:8000/auth/register"
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }

    req = urllib.request.Request(url, method="OPTIONS")
    for k, v in headers.items():
        req.add_header(k, v)

    try:
        print(f"Sending OPTIONS request to {url}...")
        with urllib.request.urlopen(req) as response:
            print(f"Status Code: {response.status}")
            print(f"Headers: {response.headers}")
            print("OPTIONS request succeeded.")

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(f"Headers: {e.headers}")
        if e.code == 400:
            print("Reproduced 400 Bad Request on OPTIONS.")

    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}. Is the server running?")


if __name__ == "__main__":
    test_options_request()
