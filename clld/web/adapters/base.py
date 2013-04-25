from zope.interface import implementer, implementedBy
from pyramid.response import Response
from pyramid.renderers import render as pyramid_render

from clld import interfaces


class Renderable(object):
    """Virtual base class for adapters

    Adapters can provide custom behaviour either by specifying a template to use for
    rendering, or by overwriting the render method.
    """
    template = None
    mimetype = 'text/plain'
    extension = None
    send_mimetype = None

    def __init__(self, obj):
        self.obj = obj

    @property
    def charset(self):
        return 'utf-8' \
            if self.mimetype.startswith('text/') \
            or 'xml' in self.mimetype \
            or 'kml' in self.mimetype \
            else None

    def render_to_response(self, ctx, req):
        res = Response(self.render(ctx, req))
        res.content_type = self.send_mimetype or self.mimetype
        if self.charset:
            res.content_type += '; charset=%s' % self.charset
        return res

    def render(self, ctx, req):
        return pyramid_render(self.template, {'ctx': ctx}, request=req)


@implementer(interfaces.IRepresentation)
class Representation(Renderable):
    """Base class for adapters implementing IRepresentation
    """
    pass


@implementer(interfaces.IIndex)
class Index(Renderable):
    """Base class for adapters implementing IIndex
    """
    pass