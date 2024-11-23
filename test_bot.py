from unittest.mock import AsyncMock

def test_load_last_execution_dates_missing_file():
    if os.path.exists('last_execution_dates.json'):
        os.remove('last_execution_dates.json')
    result = load_last_execution_dates()
    assert result == {'last_poll_date': None, 'last_notification_date': None}

def test_load_last_execution_dates_valid_file():
    # Create a mock JSON file
    with open('last_execution_dates.json', 'w') as f:
        json.dump({
            'last_poll_date': '2024-01-01',
            'last_notification_date': '2024-01-02'
        }, f)

    result = load_last_execution_dates()
    assert result['last_poll_date'] == datetime(2024, 1, 1).date()
    assert result['last_notification_date'] == datetime(2024, 1, 2).date()


def test_create_poll(mocker):
    mock_channel = mocker.MagicMock()
    mock_channel.send = AsyncMock(return_value=mocker.MagicMock())

    # Call the function
    asyncio.run(create_poll(mock_channel))

    # Assert that the poll message was sent
    mock_channel.send.assert_called_once_with(mocker.ANY)

def test_on_ready_missing_env_var(mocker):
    mocker.patch.dict(os.environ, {}, clear=True)
    with pytest.raises(SystemExit):
        asyncio.run(on_ready())

def test_reaction_alignment_error(mocker):
    mocker.patch("bot.poll_options", ["Yes", "No", "Maybe"])  # Three options
    mocker.patch("bot.emojis", ["👍", "👎"])  # Two emojis
    mock_channel = mocker.MagicMock()

    with pytest.raises(AssertionError):
        asyncio.run(create_poll(mock_channel))

def test_initialize_execution_dates():
    if os.path.exists('last_execution_dates.json'):
        os.remove('last_execution_dates.json')
    initialize_execution_dates()
    assert os.path.exists('last_execution_dates.json')
