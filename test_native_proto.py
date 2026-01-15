
import requests
import sys
import struct

def encode_varint(value):
    buf = bytearray()
    while value >= 0x80:
        buf.append((value & 0x7F) | 0x80)
        value >>= 7
    buf.append(value)
    return buf

def create_field(field_num, wire_type, content):
    tag = (field_num << 3) | wire_type
    return encode_varint(tag) + content

def create_string_field(field_num, text):
    content = text.encode('utf-8')
    return create_field(field_num, 2, encode_varint(len(content)) + content)

def create_varint_field(field_num, value):
    return create_field(field_num, 0, encode_varint(value))

def create_message_field(field_num, message_bytes):
    return create_field(field_num, 2, encode_varint(len(message_bytes)) + message_bytes)

def test_native_proto(access_token):
    # 1. Construct ClientMetadata
    # IdeType: ANTIGRAVITY = 9
    client_metadata = create_varint_field(1, 9)
    # ide_version = "0.44.11"
    client_metadata += create_string_field(2, "0.44.11")
    # plugin_version = "0.44.11"
    client_metadata += create_string_field(3, "0.44.11")
    # Platform: DARWIN_ARM64 = 2 (Assuming Mac ARM)
    client_metadata += create_varint_field(4, 2)
    # update_channel = "stable" (Guessing, maybe optional)
    # client_metadata += create_string_field(5, "stable") 
    # PluginType: GEMINI = 2
    client_metadata += create_varint_field(7, 2)
    # ide_name = "Antigravity"
    client_metadata += create_string_field(8, "Antigravity")

    # 2. Construct OnboardUserRequest
    # tier_id = "" (Field 1)
    onboard_request = create_string_field(1, "")
    # metadata = client_metadata (Field 3)
    onboard_request += create_message_field(3, client_metadata)
    
    # 3. Connect-RPC Envelope?
    # Usually Connect-RPC over HTTP/1.1 with application/connect+proto 
    # just sends the raw proto message as body.
    # Note: Connect-RPC usually prefixes with 5 bytes (flag + length) for gRPC-Web/streaming,
    # but for Unary over HTTP, it might just be the raw body.
    # Let's try raw body first.
    
    url = "https://cloudcode-pa.googleapis.com/v1internal:onboardUser"
    headers = {
        "Content-Type": "application/connect+proto",
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Antigravity/0.44.11 Electron/32.2.6",
        "X-Antigravity-Client-Version": "0.44.11",
        "X-Antigravity-Ide-Name": "Antigravity",
        "Connect-Protocol-Version": "1"
    }

    print(f"Sending Proto Request to {url}...")
    # print(f"Hex Dump: {onboard_request.hex()}")
    
    try:
        response = requests.post(url, data=onboard_request, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success! Response is binary proto.")
            print(f"Response Hex: {response.content.hex()[:100]}...") # Print first 100 chars
        else:
            print("Error Response:")
            print(response.text)
            print(f"Headers: {response.headers}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_native_proto.py <access_token>")
        sys.exit(1)
    
    test_native_proto(sys.argv[1])
