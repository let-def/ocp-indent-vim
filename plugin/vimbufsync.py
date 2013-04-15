import vim
import re
import os
import sys
import bisect
from itertools import groupby

changes_pattern = re.compile('(>)?\s*(\d+)\s*(\d+)\s*(\d+)\s*(.*)$')

def changes_of_buffer(nr):
  # extract result of "changes" command on specified buffer
  cmd = "let selnr = %d\n%s" % (nr,
"let curnr = bufnr('%')\n\
redir => changes_string\n\
if curnr == selnr\n\
  silent changes\n\
else\n\
  noa | execute 'buffer ' . selnr | silent changes | execute 'buffer ' . curnr\n\
endif\n\
redir END")
  try:
    vim.command(cmd)
    return vim.eval("changes_string").split("\n")
  except vim.error:
    return None

def extract_change(match):
  return (int(match.group(3)),int(match.group(4)),match.group(5))

def extract_changes(nr):
  global changes_pattern
  # compute changes as a list of match objects
  changes = changes_of_buffer(nr)
  changes = filter(None,map(changes_pattern.match,changes))
  if len(changes) == 0:
    return None
  # find current position in change list
  position = 0
  for change in changes:
    position += 1
    if change.group(1):
      break
  # drop everything after cursor
  changes = changes[:position]
  # convert to canonical format (list of (line,col,contents) tuples)
  return dict((k, len(list(v))) for k,v in groupby(sorted(map(extract_change,changes))))

class BufferRevision:
  def __init__(self, nr, rev):
    self._nr = nr
    self._rev = rev
    self._last_line = -1
    self._last_rev  = -1

  def buf(self):
    return sync_buffer(self._nr)

  def bufnr(self):
    return self._nr

  def line(self):
    buf = self.buf()
    if buf and self._last_rev != buf._revision() and self._last_line > 0:
      (self._last_line,self._last_rev) = buf._validate_revision(self._rev)
    return self._last_line

class ShadowBuffer:
  def __init__(self,nr):
    self._nr = nr
    self._rev = 0
    self.clear()

  def clear(self):
    self._rev += 1
    self._shadow = []
    self._revisions_line = []
    self._revisions_num  = []
    self._revobj = None
    self._changes = None

  def _find_changes(self):
    previous = self._changes
    changes = extract_changes(self._nr)
    self._changes = changes

    first_pass = previous == None
    if first_pass:
      return None
    if not len:
      return []
    return [k for (k,v) in changes.items()
              if not k in previous or previous[k] < v]

  def _find_changed_line(self):
    changes = self._find_changes()
    if changes == None:
      return 0
    lines = set(lin for lin,col,txt in changes) 
    if lines:
      return min(lines)
    return None

  def _revision(self):
    return self._rev

  def revision(self):
    if not (self._revobj and self.revobj._rev == self._rev):
      self._revobj = BufferRevision(self._nr, self._rev)
    return self._revobj

  def _invalidate_lines(self,line):
    self._rev += 1

    last = bisect.bisect_left(self._revisions_line, line)
    if last:
      self._revisions_line = self._revisions_line[:last]
      self._revisions_num  = self._revisions_num[:last]
    else:
      self._revisions_line = []
      self._revisions_num  = []    
    self._revisions_line.append(line)
    self._revisions_num.append(self._rev)

  def _validate_revision(self,rev):
    index = bisect.bisect_right(self._revisions_num, rev)
    if index:
      return (self._revisions_line[index],self._rev)
    else:
      return (0,self._rev)

  def sync(self):
    try:
      buf = vim.buffers[self._nr]
    except IndexError:
      return None
    line = self._find_changed_line()
    if not line:
      return self.revision()
    line = min(line,len(self._shadow),len(buf))

    # heuristic: find 3 equal non-blank lines in a row
    in_a_row = 0
    line_count = 0
    while line > 0 and in_a_row < 3:
      line -= 1
      if self._shadow[line] == buf[line]:
        line_count += 1
        if self._shadow[line] != "":
          in_a_row += 1
      else:
        in_a_row = 0
        line_count = 0
    line += 1 + line_count

    # update shadow buffer
    if line < 1:
      self._shadow[:] = buf[:]
    else:
      self._shadow[line-1:] = buf[line-1:]

    # new revision
    self._invalidate_lines(line)
    return self.revision()

shadow_buffers = dict()

def sync_buffer(nr):
  global shadow_buffers
  try:
    buf = vim.buffers[nr]
    if not (nr in shadow_buffers):
      # Garbage collect deleted buffers
      for nr in shadow_buffers:
        try:
          vim.buffers[nr]
        except IndexError:
          del shadow_buffers[nr]
      shadow_buffers[nr] = ShadowBuffer(nr)
    return shadow_buffers[nr]
  except IndexError:
    if nr in shadow_buffers: del shadow_buffers[nr]
    return None

def sync(nr=None):
  if not nr:
    nr = vim.current.buffer.number
  buf = sync_buffer(nr)
  if buf: return buf.sync()
  return None
