let s:current_dir=expand("<sfile>:p:h")
py import sys, vim
py if not vim.eval("s:current_dir") in sys.path:
\    sys.path.append(vim.eval("s:current_dir"))

call vimbufsync#init()
py import merlindent

function! merlindent#init()
endfunction

function! merlindent#OcpIndentLine()
  py vim.command("let l:ret = %d" % merlindent.vim_indentline())
  return l:ret
endfunction
