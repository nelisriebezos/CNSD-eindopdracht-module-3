import json
from unittest.mock import patch, MagicMock
import os


@patch.dict(os.environ, {"DISABLE_XRAY": "True", "EVENT_BUS_ARN": ""})
def test_ping_pong():
    # Mock EventBridge client
    with patch('boto3.client') as mock_client:
        mock_event_bridge = MagicMock()
        mock_client.return_value = mock_event_bridge

        # Invoke the lambda handler
        from functions.Ping.app import lambda_handler
        response = lambda_handler({}, {})

        # Verify put_events was called
        assert mock_event_bridge.put_events.call_count == 1

        # Assert the response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body["message"] == "Pong"
