def test_load_last_execution_dates_missing_file():
    if os.path.exists('last_execution_dates.json'):
        os.remove('last_execution_dates.json')
    result = load_last_execution_dates()
    assert result == {'last_poll_date': None, 'last_notification_date': None}
