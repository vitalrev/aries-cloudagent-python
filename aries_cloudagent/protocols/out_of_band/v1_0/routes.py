"""Connection handling admin routes."""

import json
import logging

from aiohttp import web
from aiohttp_apispec import docs, request_schema

from aries_cloudagent.storage.error import StorageNotFoundError

from marshmallow import fields, Schema

from .manager import OutOfBandManager

from .messages.invitation import InvitationSchema


LOGGER = logging.getLogger(__name__)


class InvitationCreateRequestSchema(Schema):
    class AttachmentDefSchema(Schema):
        _id = fields.String(data_key="id")
        _type = fields.String(data_key="type")

    attachments = fields.Nested(AttachmentDefSchema, many=True, required=False)
    include_handshake = fields.Boolean(default=False)
    use_public_did = fields.Boolean(default=False)


class InvitationSchema(InvitationSchema):
    service = fields.Field()


@docs(
    tags=["out-of-band"], summary="Create a new connection invitation",
)
@request_schema(InvitationCreateRequestSchema())
async def invitation_create(request: web.BaseRequest):
    """
    Request handler for creating a new connection invitation.

    Args:
        request: aiohttp request object

    Returns:
        The out of band invitation details

    """
    context = request.app["request_context"]

    body = await request.json()

    attachments = body.get("attachments")
    include_handshake = body.get("include_handshake")
    use_public_did = body.get("use_public_did")
    multi_use = json.loads(request.query.get("multi_use", "false"))
    # base_url = context.settings.get("invite_base_url")

    oob_mgr = OutOfBandManager(context)

    try:
        invitation = await oob_mgr.create_invitation(
            multi_use=multi_use,
            attachments=attachments,
            include_handshake=include_handshake,
            use_public_did=use_public_did,
        )
    except StorageNotFoundError:
        raise web.HTTPBadRequest()

    return web.json_response(invitation.serialize())


@docs(
    tags=["out-of-band"], summary="Create a new connection invitation",
)
# @request_schema(InvitationSchema())
async def invitation_receive(request: web.BaseRequest):
    """
    Request handler for creating a new connection invitation.

    Args:
        request: aiohttp request object

    Returns:
        The out of band invitation details

    """
    context = request.app["request_context"]
    body = await request.json()

    oob_mgr = OutOfBandManager(context)

    invitation = await oob_mgr.receive_invitation(invitation=body)

    return web.json_response(invitation.serialize())


async def register(app: web.Application):
    """Register routes."""
    app.add_routes(
        [
            # web.get("/out-of-band", invitation_list),
            # web.get("/out-of-band/{id}", invitation_retrieve),
            web.post("/out-of-band/create-invitation", invitation_create),
            web.post("/out-of-band/receive-invitation", invitation_receive),
        ]
    )
