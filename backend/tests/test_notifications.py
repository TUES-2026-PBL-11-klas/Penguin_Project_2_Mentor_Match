import pytest
from unittest.mock import MagicMock, patch
from app.notifications.service import WebPushNotificationService

@pytest.fixture
def notification_service():
    return WebPushNotificationService("fake_key", {"sub": "mailto:test@test.com"})

@pytest.fixture
def mock_db():
    return MagicMock()

def test_save_subscription_new(notification_service, mock_db):
    sub_info = {
        "endpoint": "https://push.com/abc",
        "keys": {"auth": "auth_key", "p256dh": "p256"}
    }
    mock_db.scalars().first.return_value = None
    
    sub = notification_service.save_subscription(mock_db, user_id=1, sub_info=sub_info)
    
    assert sub.endpoint == "https://push.com/abc"
    assert sub.user_id == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_save_subscription_existing(notification_service, mock_db):
    sub_info = {
        "endpoint": "https://push.com/abc",
        "keys": {"auth": "new_auth", "p256dh": "new_p256"}
    }
    existing_sub = MagicMock()
    existing_sub.endpoint = "https://push.com/abc"
    mock_db.scalars().first.return_value = existing_sub
    
    sub = notification_service.save_subscription(mock_db, user_id=1, sub_info=sub_info)
    
    assert existing_sub.auth == "new_auth"
    assert existing_sub.p256dh == "new_p256"
    assert mock_db.add.call_count == 0  # Did not add new
    mock_db.commit.assert_called_once()

@patch('app.notifications.service.executor')
def test_send_notification_integration(mock_executor, notification_service, mock_db):
    """Integration style test verifying the async queue behavior combined with DB models."""
    mock_sub = MagicMock()
    mock_sub.endpoint = "test_end"
    mock_sub.p256dh = "test_p256"
    mock_sub.auth = "test_auth"
    
    mock_db.scalars().all.return_value = [mock_sub]
    
    notification_service.send_notification(mock_db, user_id=1, title="Test", message="Msg", type="Alert")
    
    # Assert Notification model was tracked in DB transaction
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    
    # Assert Async Executor dispatch was trigged accurately
    mock_executor.submit.assert_called_once()
    

def test_get_user_notifications(notification_service, mock_db):
    mock_notif = MagicMock()
    mock_notif.id = 1
    mock_notif.type = "Alert"
    mock_notif.message = "Hello test"
    mock_notif.is_read = False
    mock_notif.session_id = None
    
    class MockResult:
        def all(self):
            return [mock_notif]
            
    mock_db.scalars.return_value = MockResult()
    
    res = notification_service.get_user_notifications(mock_db, user_id=1)
    
    assert len(res) == 1
    assert res[0]["message"] == "Hello test"
