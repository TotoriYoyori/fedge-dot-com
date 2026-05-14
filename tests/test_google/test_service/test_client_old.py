# from datetime import UTC, datetime, timedelta
# from types import SimpleNamespace
# from unittest.mock import AsyncMock, Mock, patch
#
# import pytest
#
# from src.google.exceptions import ClientSecretNotFound, FaultyFlow, InvalidPKCE
# from src.google.models import GoogleOAuthCredential, GoogleOAuthState
# from src.google.schemas import GoogleOAuth2CredentialCreate
# from src.google.service.client import (
#     _attach_pkce,
#     _coerce_utc_datetime,
#     _convert_credential,
#     _fetch_base_flow,
#     credential_is_stale,
#     fetch_google_oauth_credential,
#     fetch_google_oauth_state,
#     get_gmail_service,
#     refresh_google_oauth_credential,
#     state_is_stale,
# )
#
#
# class TestCoerceUtcDatetime:
#     def test_happy_path_converts_aware_datetime_to_utc(self) -> None:
#         aware_value = datetime(2026, 5, 6, 12, 0, tzinfo=UTC)
#
#         assert _coerce_utc_datetime(aware_value) == aware_value
#
#     def test_missing_value_returns_none(self) -> None:
#         assert _coerce_utc_datetime(None) is None
#
#     def test_junk_value_normalizes_naive_datetime(self) -> None:
#         naive_value = datetime(2026, 5, 6, 12, 0)
#
#         assert _coerce_utc_datetime(naive_value) == naive_value.replace(tzinfo=UTC)
#
#
# class TestFetchBaseFlow:
#     def test_returns_google_flow(self) -> None:
#         mock_flow = Mock()
#
#         with patch(
#             "src.google.service.client.Flow.from_client_secrets_file",
#             return_value=mock_flow,
#         ) as mock_from_client_secrets_file:
#             result = _fetch_base_flow()
#
#         assert result is mock_flow
#         mock_from_client_secrets_file.assert_called_once()
#
#     def test_missing_client_secret_file(self) -> None:
#         with (
#             patch("src.google.service.client.Flow.from_client_secrets_file", side_effect=FileNotFoundError),
#             pytest.raises(ClientSecretNotFound),
#         ):
#             _fetch_base_flow()
#
#
# class TestAttachPkce:
#     def test_attaches_state_and_code_verifier(self) -> None:
#         flow = Mock()
#
#         result = _attach_pkce(flow, "oauth-state", "code-verifier")
#
#         assert result is flow
#         assert flow.state == "oauth-state"
#         assert flow.code_verifier == "code-verifier"
#
#     @pytest.mark.parametrize("code_verifier", [None, ""])
#     def test_missing_code_verifier(self, code_verifier: str | None) -> None:
#         with pytest.raises(InvalidPKCE):
#             _attach_pkce(Mock(), "oauth-state", code_verifier)
#
#
# class TestConvertCredential:
#     def test_happy_path_builds_google_credentials(self, oauth_credential) -> None:
#         new_credential = _convert_credential(oauth_credential)
#
#         assert new_credential.token == oauth_credential.access_token
#         assert new_credential.refresh_token == oauth_credential.refresh_token
#         assert new_credential.scopes == oauth_credential.scopes.split(",")
#         assert new_credential.expiry == oauth_credential.expiry
#
#     def test_missing_expiry_leaves_google_credentials_without_expiry(self) -> None:
#         current_credential = GoogleOAuth2CredentialCreate(
#             user_id=1,
#             access_token="access-token",
#             refresh_token="refresh-token",
#             token_uri="https://oauth2.googleapis.com/token",
#             client_id="client-id",
#             client_secret="client-secret",
#             scopes="scope-a,scope-b",
#             expiry=None,
#             email_address="merchant@example.com",
#         )
#
#         new_credential = _convert_credential(current_credential)
#
#         assert new_credential.expiry is None
#
#     def test_junk_expiry_normalizes_naive_expiry_to_utc(self) -> None:
#         expiry = datetime.now() + timedelta(hours=1)
#         current_credential = GoogleOAuthCredential(
#             user_id=1,
#             access_token="access-token",
#             refresh_token="refresh-token",
#             token_uri="https://oauth2.googleapis.com/token",
#             client_id="client-id",
#             client_secret="client-secret",
#             scopes="scope-a,scope-b",
#             expiry=expiry,
#             email_address="merchant@example.com",
#             created_time=datetime.now(UTC),
#             updated_time=datetime.now(UTC),
#         )
#
#         new_credential = _convert_credential(current_credential)
#
#         assert new_credential.expiry == expiry.replace(tzinfo=UTC)
#
#
# class TestFetchGoogleOauthState:
#     def test_happy_path_returns_state_payload(self, valid_user) -> None:
#         mock_flow = Mock()
#         mock_flow.code_verifier = "code-verifier"
#         mock_flow.authorization_url.return_value = ("https://example.com/auth", "state-123")
#
#         with patch("src.google.service.client._fetch_base_flow", return_value=mock_flow):
#             result = fetch_google_oauth_state(valid_user)
#
#         assert result.auth_url == "https://example.com/auth"
#         assert result.state == "state-123"
#         assert result.user_id == valid_user.id
#         assert result.code_verifier == "code-verifier"
#
#     def test_junk_flow_raises_faulty_flow(self, valid_user) -> None:
#         mock_flow = Mock()
#         mock_flow.authorization_url.side_effect = RuntimeError("bad flow")
#
#         with (
#             patch("src.google.service.client._fetch_base_flow", return_value=mock_flow),
#             pytest.raises(FaultyFlow),
#         ):
#             fetch_google_oauth_state(valid_user)
#
#
# class TestStateIsStale:
#     def test_happy_path_returns_false_for_fresh_state(self) -> None:
#         oauth_state = GoogleOAuthState(
#             state="test-state",
#             auth_url="https://accounts.google.com/o/oauth2/auth",
#             user_id=1,
#             code_verifier="verifier",
#             created_time=datetime.now(UTC),
#         )
#
#         assert state_is_stale(oauth_state) is False
#
#     def test_missing_timezone_accepts_naive_created_time(self) -> None:
#         stale_created_time = datetime.now() - timedelta(days=1)
#         oauth_state = GoogleOAuthState(
#             state="test-state",
#             auth_url="https://accounts.google.com/o/oauth2/auth",
#             user_id=1,
#             code_verifier="verifier",
#             created_time=stale_created_time,
#         )
#
#         assert state_is_stale(oauth_state) is True
#
#
# class TestFetchGoogleOauthCredential:
#     async def test_happy_path_returns_credential_payload(self, oauth_state) -> None:
#         new_credential = SimpleNamespace(
#             token="new-access-token",
#             refresh_token="new-refresh-token",
#             token_uri="https://oauth2.googleapis.com/token",
#             client_id="client-id",
#             client_secret="client-secret",
#             scopes=["scope-a", "scope-b"],
#             expiry=datetime.now(UTC) + timedelta(hours=1),
#         )
#         verified_flow = Mock()
#         verified_flow.new_credential = new_credential
#
#         with (
#             patch("src.google.service.client._fetch_base_flow", return_value=Mock()),
#             patch("src.google.service.client._attach_pkce", return_value=verified_flow),
#         ):
#             result = await fetch_google_oauth_credential("exchange-code", oauth_state)
#
#         assert result.user_id == oauth_state.user_id
#         assert result.access_token == "new-access-token"
#         assert result.refresh_token == "new-refresh-token"
#         assert result.scopes == "scope-a,scope-b"
#         verified_flow.fetch_token.assert_called_once_with(code="exchange-code")
#
#     async def test_missing_pkce_raises(self, oauth_state) -> None:
#         with (
#             patch("src.google.service.client._fetch_base_flow", return_value=Mock()),
#             patch(
#                 "src.google.service.client._attach_pkce",
#                 side_effect=InvalidPKCE,
#             ),
#             pytest.raises(InvalidPKCE),
#         ):
#             await fetch_google_oauth_credential("exchange-code", oauth_state)
#
#     async def test_junk_exchange_code_raises_faulty_flow(self, oauth_state) -> None:
#         verified_flow = Mock()
#         verified_flow.fetch_token.side_effect = RuntimeError("bad token")
#
#         with (
#             patch("src.google.service.client._fetch_base_flow", return_value=Mock()),
#             patch("src.google.service.client._attach_pkce", return_value=verified_flow),
#             pytest.raises(FaultyFlow),
#         ):
#             await fetch_google_oauth_credential("junk-code", oauth_state)
#
#
# class TestRefreshGoogleOauthCredential:
#     async def test_happy_path_returns_updated_credential(self, oauth_credential) -> None:
#         refreshed_expiry = datetime.now(UTC) + timedelta(hours=2)
#         new_credential = Mock()
#         new_credential.expired = True
#         new_credential.token = "refreshed-access-token"
#         new_credential.refresh_token = "refreshed-refresh-token"
#         new_credential.token_uri = "https://oauth2.googleapis.com/token"
#         new_credential.client_id = "client-id"
#         new_credential.client_secret = "client-secret"
#         new_credential.scopes = ["scope-a", "scope-b"]
#         new_credential.expiry = refreshed_expiry
#         new_credential.refresh = Mock()
#         mock_refresh = AsyncMock()
#
#         with (
#             patch("src.google.service.client._convert_credential", return_value=new_credential),
#             patch("src.google.service.client.asyncer.asyncify", return_value=mock_refresh),
#         ):
#             result = await refresh_google_oauth_credential(oauth_credential)
#
#         assert isinstance(result, GoogleOAuth2CredentialCreate)
#         assert result.access_token == "refreshed-access-token"
#         assert result.refresh_token == "refreshed-refresh-token"
#         assert result.scopes == "scope-a,scope-b"
#         assert result.expiry == refreshed_expiry
#         mock_refresh.assert_awaited_once()
#
#     async def test_missing_expiration_returns_none(self, oauth_credential) -> None:
#         new_credential = Mock()
#         new_credential.expired = False
#
#         with patch("src.google.service.client._convert_credential", return_value=new_credential):
#             result = await refresh_google_oauth_credential(oauth_credential)
#
#         assert result is None
#
#     async def test_junk_refresh_that_changes_nothing_returns_none(self, oauth_credential) -> None:
#         new_credential = Mock()
#         new_credential.expired = True
#         new_credential.token = oauth_credential.access_token
#         new_credential.refresh_token = oauth_credential.refresh_token
#         new_credential.token_uri = oauth_credential.token_uri
#         new_credential.client_id = oauth_credential.client_id
#         new_credential.client_secret = oauth_credential.client_secret
#         new_credential.scopes = oauth_credential.scopes.split(",")
#         new_credential.expiry = oauth_credential.expiry
#         new_credential.refresh = Mock()
#         mock_refresh = AsyncMock()
#
#         with (
#             patch("src.google.service.client._convert_credential", return_value=new_credential),
#             patch("src.google.service.client.asyncer.asyncify", return_value=mock_refresh),
#         ):
#             result = await refresh_google_oauth_credential(oauth_credential)
#
#         assert result is None
#         mock_refresh.assert_awaited_once()
#
#
# class TestCredentialIsStale:
#     async def test_happy_path_returns_true_for_expired_unrefreshable_credential(
#         self, oauth_credential
#     ) -> None:
#         new_credential = Mock()
#         new_credential.expired = True
#         new_credential.refresh_token = None
#
#         with patch("src.google.service.client._convert_credential", return_value=new_credential):
#             result = await credential_is_stale(oauth_credential)
#
#         assert result is True
#
#     async def test_missing_refresh_token_on_fresh_credential_returns_false(
#         self, oauth_credential
#     ) -> None:
#         new_credential = Mock()
#         new_credential.expired = False
#         new_credential.refresh_token = None
#
#         with patch("src.google.service.client._convert_credential", return_value=new_credential):
#             result = await credential_is_stale(oauth_credential)
#
#         assert result is False
#
#     async def test_junk_refresh_token_on_expired_credential_returns_false(
#         self, oauth_credential
#     ) -> None:
#         new_credential = Mock()
#         new_credential.expired = True
#         new_credential.refresh_token = "refresh-token"
#
#         with patch("src.google.service.client._convert_credential", return_value=new_credential):
#             result = await credential_is_stale(oauth_credential)
#
#         assert result is False
#
#
# class TestGetGmailService:
#     def test_happy_path_builds_gmail_service(self, oauth_credential) -> None:
#         converted_credentials = Mock()
#         mock_service = Mock()
#
#         with (
#             patch(
#                 "src.google.service.client._convert_credential",
#                 return_value=converted_credentials,
#             ),
#             patch("src.google.service.client.build", return_value=mock_service) as mock_build,
#         ):
#             result = get_gmail_service(oauth_credential)
#
#         assert result is mock_service
#         mock_build.assert_called_once_with(
#             "gmail",
#             "v1",
#             new_credential=converted_credentials,
#             cache_discovery=False,
#         )
#
#     def test_missing_refresh_token_still_builds_service(self, oauth_credential) -> None:
#         oauth_credential.refresh_token = None
#         converted_credentials = Mock()
#
#         with (
#             patch(
#                 "src.google.service.client._convert_credential",
#                 return_value=converted_credentials,
#             ),
#             patch("src.google.service.client.build", return_value=Mock()) as mock_build,
#         ):
#             get_gmail_service(oauth_credential)
#
#         assert mock_build.called
#
