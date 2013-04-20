let s:current_dir=expand("<sfile>:p:h")
py import vim
py if not vim.eval("s:current_dir") in sys.path: sys.path.append(vim.eval("s:current_dir"))

py import merlindent
call vimbufsync#init()

function! merlindent#OcpIndentLine()
  py vim.command("let l:ret = %d" % merlindent.vim_indentline())
  return l:ret
endfunction
