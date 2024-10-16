


#Proxy.py

# For the proxy filter to work, add a set of proxies, untampered from "https://hproxy.com/". Select HTTP Proxies & United States or other desired Location.

## HTTP Codes:
200: Indicates success.
403: Could be usable depending on the target sites.
407: Requires authentication; consider usable only if you have credentials.
503: Might work at different times; consider usable but with caution.

Edit by add or removing codes in prxy.py with the appropriate line: "response.status_code in {200, 403, 407, 503}:"
