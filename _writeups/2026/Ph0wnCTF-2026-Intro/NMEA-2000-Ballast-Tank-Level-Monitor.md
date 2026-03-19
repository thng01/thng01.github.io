---
layout: writeup
category: Ph0wnCTF-2026-Intro
chall_description: 
points: 
solves: 
tags: NMEA-2000
date: 2026-03-19
comments: false
---
# NMEA-2000 Ballast Tank Challenge - Write-up

## Challenge Overview

The challenge involved connecting to a **Luxury Yacht MCP Server** at `http://34.155.95.172:9999/mcp` and retrieving a secret message by depleting the yacht's ballast tank level from 65.9% to 0%. The message was encoded as hex-encoded ASCII data within NMEA-2000 (National Marine Electronics Association) protocol packets.

**Flag:** `ph0wn{the_cR0wn_iS_sh1ning}`

## Technologies & Protocols

### 1. MCP (Model Context Protocol)

- A JSON-RPC 2.0 based protocol for client-server communication
- Uses HTTP with custom session management
- Supports "http-streamable" transport (Server-Sent Events / SSE)
- Session IDs are returned in response headers (`mcp-session-id`), not body

### 2. NMEA-2000 (N2K)

- Standard marine protocol for vessel equipment communication
- Uses CAN (Controller Area Network) bus format
- Data encoded as packets with:
  - **CAN ID**: Encodes Priority, Data Page, PGN, and Source Address
  - **Payload**: 0-8 bytes of data (hex format with spaces)

### 3. HTTP-Streamable Transport

- Requires header: `Accept: application/json, text/event-stream`
- Maintains session state across multiple POST requests
- Session ID persists in headers for subsequent requests

## Challenge Solution

### Initial Connection & Headers (Debugging)

**Problem:** Server returned 406/400 errors

**Discovery Process:**

1. Started with standard `Accept: application/json` header → 406 error
2. Tried `Accept: text/event-stream` alone → 400 error
3. **Solution:** Combined header required: `Accept: application/json, text/event-stream`

**Key Learning:** HTTP-streamable transport expects both JSON content and SSE headers

So let's try send to see the reponse.



**Problem:** 400 Bad Request - "Missing session ID"

**Debugging Steps:**

1. Initially expected session ID in JSON response body
2. Tried passing as URL parameter
3. Tried as custom header with various names
4. **Discovery:** Session ID returned in response header: `mcp-session-id`
5. Must be included in subsequent requests via same header name

**Code Pattern:**

```
# Extract from response header
session_id = response.headers.get('mcp-session-id')

# Include in subsequent requests
headers = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
    "mcp-session-id": session_id
}
```



The MCP server exposed 7 tools via `tools/list`:

- `connect` - Establish yacht connection (returns UUID)
- `disconnect` - Close yacht connection
- `get_fluid_level` - Read ballast tank level (PGN 127505)
- `get_fuel_rate` - Read fuel consumption (PGN 127489)
- `get_speed` - Read vessel speed (PGN 128259)
- `travel` - Simulate movement (PGN 128275)
- `alert` - Retrieve alert/secret message



**Initial Reading:** 65.9% tank level

**Parsing NMEA Packet:**

```
{"can_id": 435294497, "data": "00 A8 61 D0 07 00 00 FF"}
                                    ↑
                           Tank level byte

tank_level_byte = 0xA8 = 168 decimal
tank_level_percent = (168 / 255) * 100 = 65.9%
```



So now I guess we need to simulate the movement of the boat, so that the fuel level can drop. 

We bump into another problem while calling 

**Problem:** `tools/call "travel"` failed with "Not PGN 128275 frames"

**Iterative Debugging:**

1. **CAN ID Calculation Issue**
   - Started with wrong bit shifts: `(6<<26) | (1<<24) | (0xF4<<16) | (0x8B<<8)` → Wrong
   - Analyzed working CAN IDs from other tools:
     - Speed: `0x9f50323` (PGN 128259)
     - Fuel: `0x9f20123` (PGN 127489)
     - Tank: `0x19f21121` (PGN 127505)
   - **Correct Formula:** `(Priority 6 << 26) | (DP 1 << 24) | (PGN << 8) | SA`
   - **Result:** For PGN 128275: `(6<<26) | (1<<24) | (128275<<8) | 0 = 435491584`
2. **Payload Format Issue**
   - Initial error: "Not PGN 128275 frames"
   - Tried 2-frame payload → "Payload too short: 13 bytes"
   - Tried 1-frame payload → "Payload too short: 6 bytes"
   - **Breakthrough:** Three identical frames required for Distance Log PGN!
3. **Final Working Format:**

```
can_id = (6 << 26) | (1 << 24) | (128275 << 8) | 0  # = 435491584

travel_frames = json.dumps([
    {"can_id": can_id, "data": "00 10 27 00 00 00 00 00"},
    {"can_id": can_id, "data": "00 10 27 00 00 00 00 00"},
    {"can_id": can_id, "data": "00 10 27 00 00 00 00 00"}
])
```



Once tank reached 0%, `alert()` tool returned encoded message:

```
{
  "can_id": 435160866,
  "data": [
    "00 2D 51 01 01 01 37 13",
    "01 00 00 00 00 00 00 00",
    "02 00 22 22 01 00 70 68",
    "03 30 77 6E 7B 74 68 65",
    "04 5F 63 52 30 77 6E 5F",
    "05 69 53 5F 73 68 31 6E",
    "06 69 6E 67 7D 00 00 00"
  ]
}
```

**Decoding:**

- Each frame has: `[sequence_byte, data_bytes...]`
- Skip sequence byte (first byte of each frame)
- Concatenate remaining hex bytes
- Convert to ASCII

```
hex_data = ["00 2D 51 01...", "01 00 00 00...", ...]
all_hex = ""
for frame in hex_data:
    bytes_list = frame.split()
    all_hex += " ".join(bytes_list[1:])  # Skip first byte

message = bytes.fromhex(all_hex.replace(" ", "")).decode('ascii')
# Result: "ph0wn{the_cR0wn_iS_sh1ning}"
```

## [Source code](../../../assets/CTFs/Ph0wnCTF-2026-Intro/nmea_solver_ph0wn.py)

### MCP Server Characteristics

- **Name:** Luxury Yacht MCP Server
- **Version:** 1.25.0
- **Protocol:** 2024-11-05

### Session State

- **Two-level authentication:**
  1. MCP Session ID (from initialize) - persists for tool calls
  2. Yacht Session ID (from connect tool) - passed to yacht-specific tools

### Data Simulation

- Server tracks yacht state internally
- Each `travel()` call consumes ballast and fuel
- `get_fluid_level()` returns updated state
- Tank level decreases on each iteration (roughly 20-30% per travel call)

### PGN Support

The server validates:

- CAN ID format (checks PGN bits match declared PGN)
- Payload structure (PGN 128275 requires multi-frame support)
- Data freshness (sequential reads show updated values)