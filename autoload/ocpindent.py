import os
import sys
import vim
import subprocess

ocp_indent_path = "ocp-indent"

def ocp_indent(lines):
  if lines:
    if type(lines) == int:
      end = lines
      lines = "%d-%d" % (lines,lines)
    else:
      end = lines[1]
      lines = "%d-%d" % lines
  content = "\n".join(vim.current.buffer[:end] + [""])
  process = subprocess.Popen(
      [ocp_indent_path,"--lines",lines,"--numeric"],
      stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  process.stdin.write(content)
  process.stdin.close()
  answer = process.stdout.readlines()
  state = answer.pop()
  return int(state)

def vim_indentline():
  line = int(vim.eval("v:lnum"))
  return ocp_indent(line)

def vim_equal():
  r = vim.current.range
  w = vim.current.window
  pos = w.cursor
  vim.command("0,'>!%s --lines %d-" % (ocp_indent_path, r.start+1))
  w.cursor = pos
