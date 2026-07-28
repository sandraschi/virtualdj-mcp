from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from virtualdj_mcp.tools.portmanteau.show_control import setup_show_control_portmanteau


@pytest.fixture
def mcp_instance():
    mcp = FastMCP("TestMCP")
    setup_show_control_portmanteau(mcp)
    return mcp


@pytest.mark.asyncio
async def test_show_control_registration(mcp_instance):
    tools = await mcp_instance.list_tools()
    tool_names = [t.name for t in tools]
    assert "vdj_show_control" in tool_names


@pytest.mark.asyncio
@patch("virtualdj_mcp.tools.portmanteau.show_control.SimpleUDPClient")
@patch("virtualdj_mcp.tools.portmanteau.show_control.get_vdj_client")
async def test_show_control_osc_send(mock_get_vdj_client, mock_udp_client, mcp_instance):
    mock_client_instance = MagicMock()
    mock_udp_client.return_value = mock_client_instance

    result = await mcp_instance.call_tool(
        "vdj_show_control",
        arguments={
            "operation": "osc_send",
            "address": "/composition/layers/1/clips/1/connect",
            "value": 1.0,
            "host": "127.0.0.1",
            "port": 7000,
        },
    )

    assert result is not None
    mock_udp_client.assert_called_once_with("127.0.0.1", 7000)
    mock_client_instance.send_message.assert_called_once_with("/composition/layers/1/clips/1/connect", 1.0)


@pytest.mark.asyncio
@patch("virtualdj_mcp.tools.portmanteau.show_control.get_vdj_client")
async def test_show_control_os2l(mock_get_vdj_client, mcp_instance):
    mock_client = AsyncMock()
    mock_client.send_command.return_value = {"status": "success"}
    mock_get_vdj_client.return_value = mock_client

    # Test OS2L Button
    result_button = await mcp_instance.call_tool(
        "vdj_show_control", arguments={"operation": "os2l_button", "name": "fog", "enable": True}
    )
    assert result_button is not None
    mock_client.send_command.assert_any_call("os2l_button 'fog' on")

    # Test OS2L Fader
    result_fader = await mcp_instance.call_tool(
        "vdj_show_control", arguments={"operation": "os2l_fader", "name": "stroberate", "value": 50.0}
    )
    assert result_fader is not None
    mock_client.send_command.assert_any_call("os2l_fader 'stroberate' 50.0%")
