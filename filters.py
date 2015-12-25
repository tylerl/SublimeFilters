"""Custom Commands for FilterPipes."""

try:
    from FilterPipes import filterpipes  # ST3-style import
except ImportError:
    import filterpipes  # ST2-style import

import ast
import json
import re
import urllib.parse
import pprint
import zlib
import base64
#import StringIO


class JsonPrettyprintCommand(filterpipes.FilterPipesCommandBase):
    spaces = 2
    options = None
    sort_keys = False

    def filter(self, data):
        options = dict(indent=self.spaces, separators=(',', ':'),
                       sort_keys=self.sort_keys)
        if self.options:
            options.update(self.options)
        decoder = json.JSONDecoder(strict=False)
        return json.dumps(decoder.decode(data), **options)


class DeleteBlankLinesCommand(filterpipes.FilterPipesCommandBase):

    def filter(self, text):
        return '\n'.join([line for line in text.splitlines()
                          if re.match(r'\S', line)])


class UrlParseCommand(filterpipes.FilterPipesCommandBase):

    def filter(self, text):
        o = urllib.parse.urlparse(text)
        out = dict()
        for k in ['scheme', 'netloc', 'path', 'query', 'fragment']:
            v = getattr(o, k)
            if not v:
                continue
            if k == 'query':
                out['query'] = urllib.parse.parse_qs(v)
            else:
                out[k] = v
        return pprint.pformat(out, 2)


class UrlUnparseCommand(filterpipes.FilterPipesCommandBase):

    def filter(self, text):
        o = ast.literal_eval(text)
        urlobj = []
        for k in ['scheme', 'netloc', 'path', 'parameters', 'query', 'fragment']:
            v = o.get(k, None)
            if v and k == 'query':
                v = urllib.parse.urlencode(v, doseq=True)
            urlobj.append(v)
        return urllib.parse.urlunparse(urlobj)


class LinesToListCommand(filterpipes.FilterPipesCommandBase):

    def filter(self, text):
        return '[%s]' % ','.join(text.splitlines())


class ZlibPackCommand(filterpipes.FilterPipesCommandBase):
    unpack = False
    flavor = 'gzip'
    wrap = 64
    urlsafe = False
    compresslevel = 9
    encoding='utf-8'
    WBITS = {
        'deflate': -zlib.MAX_WBITS,
        'zlib': zlib.MAX_WBITS,
        'gzip': zlib.MAX_WBITS | 16,
    }
    noheader = False

    def filter(self, text):
        text = text.encode('utf-8')
        if self.unpack:
            return self._decompress(self._decode(text)).decode(self.encoding)
        return self._encode(self._compress(text))

    def _encode(self, data):
        if self.urlsafe:
            encoded = base64.urlsafe_b64encode(data)
        else:
            encoded = base64.b64encode(data)
        encoded = encoded.decode(self.encoding)
        if self.wrap:
            return '\n'.join(
                (encoded[i:i + self.wrap] for i in
                    range(0, len(encoded), self.wrap)))
        return encoded

    def _decode(self, text):
        if self.urlsafe:
            return base64.urlsafe_b64decode(text)
        return base64.b64decode(text)

    def _compress(self, data):
        c = zlib.compressobj(
            self.compresslevel, zlib.DEFLATED, self.WBITS[self.flavor])
        return c.compress(data) + c.flush()

    def _decompress(self, data):
        d = zlib.decompressobj(self.WBITS[self.flavor])
        return d.decompress(data) + d.flush()
