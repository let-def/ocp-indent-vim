import os
import sys
import vim
import time
import subprocess

ocp_indent_path = "ocp-indent"
ocp_lastline = None
ocp_lasttime = None
ocp_linefst = 0
ocp_linebuf = []
ocp_inarow = 0

def ocp_indent(lines):
  if lines:
    if type(lines) == int:
      end = lines
      lines = "%d-%d" % (lines,lines)
    else:
      end = lines[1]
      lines = "%d-%d" % lines
  end += 1

  buffer = vim.current.buffer
  content = buffer[:end]
  content = "\n".join(content)

  # Fix https://github.com/def-lkb/ocp-indent-vim/issues/4
  in_comment = content.count("(*") > content.count("*)")

  # Find end of comment (~ ignoring nested comments) or next non-empty line
  offset0 = 34
  offset1 = 55
  while end < len(buffer):
      # I like rabbits
      offset = offset0 + offset1
      offset0 = offset1
      offset1 = offset

      end0 = end
      end += offset

      padding = "\n".join(buffer[end0:end])
      content = content + "\n" + padding
      if in_comment:
          if padding.count("*)") > 0:
              break
      else:
          if padding.strip() <> "":
              break
  args = vim.eval("exists('b:ocp_indent_args') ? b:ocp_indent_args : exists ('g:ocp_indent_args') ? g:ocp_indent_args : []")
  if type(args) != list:
      args = [args]
  process = subprocess.Popen(
      [ocp_indent_path] + args + ["--lines",lines,"--numeric"],
      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open(os.devnull,"w"))
  process.stdin.write(content)
  process.stdin.close()
  return map(int,process.stdout.readlines())

def vim_contiguous(line1, line2):
  if not line1 or not line2: return False
  if line2 == line1 - 1: return True
  if line1 >= line2: return False
  if "".join(vim.current.buffer[line1+1:line2-1]).strip() == "": return True
  return False

def vim_indentline():
  global ocp_lastline, ocp_lasttime, ocp_linefst, ocp_linebuf, ocp_inarow
  line = int(vim.eval("v:lnum"))
  if vim_contiguous(ocp_lastline,line) and abs(time.time() - ocp_lasttime) < 0.1:
    # Possibly a selection indentation, use a threshold to detect consecutive calls
    if ocp_inarow > 2:
      if not (line >= ocp_linefst and line < ocp_linefst + len(ocp_linebuf)):
        ocp_linefst = line
        ocp_linebuf = ocp_indent((line, min(line + 1000, len(vim.current.buffer))))
      ocp_lasttime = time.time()
      ocp_lastline = line
      return ocp_linebuf[line - ocp_linefst]
    else:
      # Increment counter
      ocp_inarow += 1
  else:
    # Not a selection indentation
    ocp_inarow = 0

  # Current line indentation
  ocp_linebuf = []
  indent = ocp_indent(line)
  indent = indent.pop()
  ocp_lasttime = time.time()
  ocp_lastline = line
  return indent

def vim_equal():
  r = vim.current.range
  w = vim.current.window
  pos = w.cursor
  vim.command("0,'>!%s --lines %d-" % (ocp_indent_path, r.start+1))
  w.cursor = pos
