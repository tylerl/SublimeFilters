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


class JsonPrettyprintCommand(filterpipes.FilterPipesCommandBase):
  spaces = 2
  options = None
  sort_keys = False

  def filter(self, data):
    options = dict(
        indent=self.spaces, separators=(',', ':'), sort_keys=self.sort_keys)
    if self.options:
      options.update(self.options)
    decoder = json.JSONDecoder(strict=False)
    return json.dumps(decoder.decode(data), **options)


class DeleteBlankLinesCommand(filterpipes.FilterPipesCommandBase):

  def filter(self, text):
    return '\n'.join(
        [line for line in text.splitlines() if re.match(r'.*\S.*', line)])


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
  WBITS = {
      'deflate': -zlib.MAX_WBITS,
      'zlib': zlib.MAX_WBITS,
      'gzip': zlib.MAX_WBITS | 16,
  }
  noheader = False

  def filter(self, text):
    text = text.encode('utf-8')
    if self.unpack:
      return self._decompress(self._decode(text)).decode('utf-8')
    return self._encode(self._compress(text)).decode('utf-8')

  def _encode(self, data):
    if self.urlsafe:
      encoded = base64.urlsafe_b64encode(data)
    else:
      encoded = base64.b64encode(data)
    encoded = encoded.decode('utf-8')
    if self.wrap:
      return '\n'.join((encoded[i:i + self.wrap]
                        for i in range(0, len(encoded), self.wrap)))
    return encoded

  def _decode(self, text):
    if self.urlsafe:
      return base64.urlsafe_b64decode(text)
    return base64.b64decode(text)

  def _compress(self, data):
    c = zlib.compressobj(self.compresslevel, zlib.DEFLATED,
                         self.WBITS[self.flavor])
    return c.compress(data) + c.flush()

  def _decompress(self, data):
    d = zlib.decompressobj(self.WBITS[self.flavor])
    return d.decompress(data) + d.flush()


class Base64WebsafeCommand(filterpipes.FilterPipesCommandBase):
  """Base 64 encode/decode with websafe palette."""
  decode = True

  def filter(self, data):
    if self.decode:
      return base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8')
    return base64.urlsafe_b64encode(data.encode('utf-8')).decode('utf-8')


class ReverseWordsCommand(filterpipes.FilterPipesCommandBase):
  """Reverse the order of selected words. Extremely simple example."""

  def filter(self, data):
    return ' '.join(reversed(data.split(' ')))


class ProtoAssignIdsCommand(filterpipes.FilterPipesCommandBase):
  """Assign IDs to the fields in the selected protos."""
  # (optional) (string) (foo_bar) (= 2)(;)
  proto_re = r'^\s*\w+\s+\w+\s+\w+(?:\s*=\s*(?P<id>\d+))?(?P<sc>;)'

  def filter(self, data):
    lines = data.splitlines()
    taken = []
    # pass 1 to find all taken ids
    for line in lines:
      match = re.match(self.proto_re, line)
      if match:
        if match.group('id'):
          taken.append(int(match.group('id')))
    # pass 2 for output
    out = []

    def yieldnext(taken):
      n = 1
      taken = set(taken)
      while True:
        if n not in taken:
          yield n
        n += 1

    nexter = yieldnext(taken)

    for line in lines:
      match = re.match(self.proto_re, line)
      if match:
        if match.group('id'):
          out.append(line)
        else:
          out.append('%s = %i;%s' % (line[:match.start('sc')], next(nexter),
                                     line[match.end('sc'):]))
      else:
        out.append(line)
    return '\n'.join(out)


#############################3
# Printproto stuff

# class ProtoParse(object):
#   def __init__(self, text):
#     self.tf = TokenFactory(text)
#     self.prefix = self.eatspace()
#     self.msg = []

#   def ident(self):
#     self.eatspace()
#     start = self.tf.i
#     bracket = False
#     quote = False
#     if self.tf.v() == '[':
#       bracket = True
#       self.tf.next()
#     if self.tf.v() in '"\'':
#       quote = self.tf.v()
#       self.tf.next()
#     if quote:
#       self.tf.allnot(quote)
#     if bracket:
#       self.tf.allnot("]")
#     if not (quote or bracket):
#       self.allnot("[\s<{:]")

#     #if self.tf.v() in "<["

#     self.tf.allnot("[:{<]")

#   def eatspace(self):
#     return self.tf.all(r'\s')

# class TokenFactory(object):

#   def __init__(self, stream):
#     self.stream = stream
#     self.i = 0
#     self.len = len(stream)

#   def next(self):
#     n = 2 if self.stream[self.i] == '\\' else 1
#     self.i += n
#     return self.i < self.len

#   def v(self):
#     if self.stream[self.i] == '\\'
#       return self.stream[self.i:self.i+2]

#   def n(self):
#     n = 2 if self.stream[self.i] == '\\' else 1
#     try:
#       return self.stream[self.i + n]
#     except IndexError:
#       return ''

#   def all(self, pat):
#     start = self.i
#     while re.match(pat, self.v()):
#       if not self.next():
#         break
#     return self.stream[start:self.i]

#   def allnot(self, pat):
#     start = self.i
#     while not re.match(pat, self.v()):
#       if not self.next():
#         break
#     return self.stream[start:self.i]
