#!/usr/bin/env python3
import asyncio
import json
import aiohttp
from datetime import datetime

async def monitor_ballast_tank():
    """Connect to NMEA-2000 MCP server and monitor ballast tank level"""
    
    base_url = "http://34.155.95.172:9999"
    mcp_endpoint = "/mcp"
    
    try:
        # Set up headers for MCP http-streamable transport
        headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
            "User-Agent": "NMEA-2000-Monitor/1.0"
        }
        
        # Use a single session for the entire connection (important for session state)
        async with aiohttp.ClientSession() as session:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Initializing MCP session...")
            
            # Initialize with POST to get a session token
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "NMEA-2000-Monitor",
                        "version": "1.0"
                    }
                }
            }
            
            # First initialize
            async with session.post(base_url + mcp_endpoint, json=init_request, 
                                   headers={"Content-Type": "application/json", "Accept": "application/json"},
                                   timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    init_response = await response.json()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Session initialized")
                    # Extract the session ID from the mcp-session-id header!
                    session_id = response.headers.get('mcp-session-id')
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Session ID: {session_id}")
                else:
                    error_body = await response.text()
                    print(f"Failed to initialize: {response.status} - {error_body}")
                    return
            
            # Now connect to the streaming endpoint via Server-Sent Events
            # The session should maintain state from the initialization
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Connected to NMEA-2000 MCP Server")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring Ballast Tank Level...\n")
            
            # For http-streamable, we keep the same session and make streaming requests
            # Try to get list of resources to establish the stream
            list_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/list",
                "params": {}
            }
            
            sse_headers = {
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "mcp-session-id": session_id  # Use the session ID from the header
            }
            
            # POST the resources/list request with streaming response
            async with session.post(base_url + mcp_endpoint, json=list_request, headers=sse_headers,
                                  timeout=aiohttp.ClientTimeout(total=None)) as response:
                if response.status != 200:
                    error_body = await response.text()
                    print(f"Failed to connect to stream: {response.status}")
                    print(f"Response: {error_body}")
                    return
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Receiving Server-Sent Events...\n")
                
                # Parse Server-Sent Events
                # First event was resources list, now try to get tools
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/list",
                    "params": {}
                }
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Listing available tools...")
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/list",
                    "params": {}
                }
                
                async with session.post(base_url + mcp_endpoint, json=tools_request, headers=sse_headers,
                                      timeout=aiohttp.ClientTimeout(total=10)) as tools_response:
                    if tools_response.status == 200:
                        tools_data = await tools_response.json()
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Tools loaded\n")
                
                # First, call the connect tool to get a yacht session ID
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to yacht...")
                connect_request = {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "connect",
                        "arguments": {}
                    }
                }
                
                async with session.post(base_url + mcp_endpoint, json=connect_request, headers=sse_headers,
                                      timeout=aiohttp.ClientTimeout(total=10)) as connect_response:
                    if connect_response.status == 200:
                        connect_data = await connect_response.json()
                        if 'result' in connect_data:
                            result = connect_data['result']
                            if isinstance(result, dict) and result.get('content'):
                                yacht_session_id_text = result['content'][0].get('text', session_id)
                                # Strip quotes if they exist
                                yacht_session_id = yacht_session_id_text.strip('"')
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Yacht Session ID: {yacht_session_id}\n")
                            else:
                                yacht_session_id = str(result) if result else session_id
                                yacht_session_id = yacht_session_id.strip('"')
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Yacht Session ID: {yacht_session_id}\n")
                        else:
                            yacht_session_id = session_id
                    else:
                        yacht_session_id = session_id
                
                # Now use the yacht session ID to read ballast tank data continuously
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Reading ballast tank data...\n")
                request_id = 5
                
                # First get speed and fuel rate for travel simulation
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Getting speed data...")
                speed_request = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": "tools/call",
                    "params": {
                        "name": "get_speed",
                        "arguments": {
                            "session_id": yacht_session_id
                        }
                    }
                }
                
                speed_data_str = None
                async with session.post(base_url + mcp_endpoint, json=speed_request, headers=sse_headers,
                                      timeout=aiohttp.ClientTimeout(total=10)) as speed_response:
                    if speed_response.status == 200:
                        speed_data = await speed_response.json()
                        if 'result' in speed_data:
                            result = speed_data['result']
                            if isinstance(result, dict) and result.get('content'):
                                speed_data_str = result['content'][0].get('text', '')
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Speed: {speed_data_str}")
                
                request_id += 1
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Getting fuel rate data...")
                fuel_request = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": "tools/call",
                    "params": {
                        "name": "get_fuel_rate",
                        "arguments": {
                            "session_id": yacht_session_id
                        }
                    }
                }
                
                fuel_data_str = None
                async with session.post(base_url + mcp_endpoint, json=fuel_request, headers=sse_headers,
                                      timeout=aiohttp.ClientTimeout(total=10)) as fuel_response:
                    if fuel_response.status == 200:
                        fuel_data = await fuel_response.json()
                        if 'result' in fuel_data:
                            result = fuel_data['result']
                            if isinstance(result, dict) and result.get('content'):
                                fuel_data_str = result['content'][0].get('text', '')
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Fuel Rate: {fuel_data_str}\n")
                
                request_id += 1
                
                while True:
                    try:
                        # First, simulate travel to consume fuel/ballast
                        # PGN 128275 = Distance Log (0x1f513)
                        # CAN ID = (Priority 6 << 26) | (DP 1 << 24) | (PGN 128275 << 8) | SA 0 = 435491584
                        can_id = (6 << 26) | (1 << 24) | (128275 << 8) | 0
                        
                        # Need 3 frames of Distance Log packets to trigger travel
                        travel_frames_data = [
                            {"can_id": can_id, "data": "00 10 27 00 00 00 00 00"},
                            {"can_id": can_id, "data": "00 10 27 00 00 00 00 00"},
                            {"can_id": can_id, "data": "00 10 27 00 00 00 00 00"}
                        ]
                        
                        travel_frames = json.dumps(travel_frames_data)
                        
                        travel_request = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "method": "tools/call",
                            "params": {
                                "name": "travel",
                                "arguments": {
                                    "session_id": yacht_session_id,
                                    "frames": travel_frames
                                }
                            }
                        }
                        
                        travel_result = False
                        async with session.post(base_url + mcp_endpoint, json=travel_request, headers=sse_headers,
                                              timeout=aiohttp.ClientTimeout(total=10)) as travel_response:
                            if travel_response.status == 200:
                                travel_data = await travel_response.json()
                                if 'result' in travel_data:
                                    result = travel_data['result']
                                    # Check different response formats
                                    if isinstance(result, dict):
                                        if 'content' in result:
                                            travel_text = result['content'][0].get('text', 'false').lower()
                                            travel_result = 'true' in travel_text
                                        elif 'isError' not in result:
                                            travel_result = True
                                    else:
                                        travel_result = str(result).lower() == 'true'
                                elif 'error' in travel_data:
                                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Travel Error: {travel_data['error']}")
                        
                        request_id += 1
                        
                        # Now check fluid level
                        tool_request = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "method": "tools/call",
                            "params": {
                                "name": "get_fluid_level",
                                "arguments": {
                                    "session_id": yacht_session_id
                                }
                            }
                        }
                        
                        async with session.post(base_url + mcp_endpoint, json=tool_request, headers=sse_headers,
                                              timeout=aiohttp.ClientTimeout(total=10)) as read_response:
                            if read_response.status == 200:
                                data = await read_response.json()
                                
                                # Handle tool response format
                                if 'result' in data:
                                    result = data['result']
                                    
                                    # The result might be a dict with 'content' and 'isError'
                                    if isinstance(result, dict):
                                        if result.get('isError'):
                                            error_text = result.get('content', [{}])[0].get('text', 'Unknown error')
                                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Tool Error: {error_text}")
                                        else:
                                            # Extract text from content
                                            content = result.get('content', [{}])
                                            if content and isinstance(content, list):
                                                text = content[0].get('text', '')
                                                timestamp = datetime.now().strftime('%H:%M:%S')
                                                
                                                # Try to parse as JSON for NMEA data
                                                try:
                                                    nmea_data = json.loads(text)
                                                    if isinstance(nmea_data, dict) and 'data' in nmea_data:
                                                        payload = nmea_data['data']
                                                        hex_bytes = payload.split()
                                                        if len(hex_bytes) > 1:
                                                            tank_level_byte = int(hex_bytes[1], 16)
                                                            tank_level = (tank_level_byte / 255) * 100
                                                            
                                                            travel_status = "✓ Travel" if travel_result else "✗ No Travel"
                                                            print(f"[{timestamp}] ★ Ballast Tank Level: {tank_level:.1f}% [{travel_status}] - {text}")
                                                            
                                                            if tank_level <= 0:
                                                                print(f"\n[{timestamp}] ⚠️  ALERT: Ballast tank is EMPTY!")
                                                                print(f"[{timestamp}] 🔓 SECRET MESSAGE UNLOCKED!")
                                                                # Try to get alert for secret message
                                                                alert_request = {
                                                                    "jsonrpc": "2.0",
                                                                    "id": request_id + 1,
                                                                    "method": "tools/call",
                                                                    "params": {
                                                                        "name": "alert",
                                                                        "arguments": {
                                                                            "session_id": yacht_session_id
                                                                        }
                                                                    }
                                                                }
                                                                
                                                                async with session.post(base_url + mcp_endpoint, json=alert_request, headers=sse_headers,
                                                                                      timeout=aiohttp.ClientTimeout(total=10)) as alert_response:
                                                                    if alert_response.status == 200:
                                                                        alert_data = await alert_response.json()
                                                                        if 'result' in alert_data:
                                                                            alert_result = alert_data['result']
                                                                            if isinstance(alert_result, dict) and alert_result.get('content'):
                                                                                secret = alert_result['content'][0].get('text', '')
                                                                                print(f"[{timestamp}] {secret}\n")
                                                                break  # Exit after tank is empty
                                                            elif tank_level <= 10:
                                                                print(f"[{timestamp}] ⚠️  WARNING: Ballast tank level critically low!\n")
                                                except (json.JSONDecodeError, ValueError, KeyError, IndexError):
                                                    pass
                                    else:
                                        # Result is a string
                                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {result}")
                                        
                                elif 'error' in data:
                                    error = data['error']
                                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {error.get('message', 'Unknown error')}")
                        
                        request_id += 1
                        await asyncio.sleep(1)  # Check every second for faster tank depletion
                        
                    except asyncio.TimeoutError:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Request timeout")
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")
                        await asyncio.sleep(1)
                
    except aiohttp.ClientConnectorError as e:
        print(f"Failed to connect to server: {e}")
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("NMEA-2000 Ballast Tank Level Monitor")
    print("=" * 50)
    
    asyncio.run(monitor_ballast_tank())
