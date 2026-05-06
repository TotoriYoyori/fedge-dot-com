import asyncer

from googleapiclient.discovery import Resource


async def get_authorized_email(service: Resource) -> str | None:
    stmt = service.users().getProfile(userId="me")
    profile = await asyncer.asyncify(stmt.execute)()

    return profile.get("emailAddress")
