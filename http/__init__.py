"""
Module containing all HTTP related classes

Use this module (instead of the more specific ones) when importing Headers,
Request and Response outside this module.
"""

from headers import Headers

from request import Request
from request.form import FormRequest
from request.rpc import XmlRpcRequest

from response import Response
from response.html import HtmlResponse
from response.xml import XmlResponse
from response.text import TextResponse
