let s:current_dir=expand("<sfile>:p:h")
py import vim
py sys.path.insert(0, vim.eval("s:current_dir"))
py import merlindent

function! merlindent#OcpIndentLine()
  py vim.command("let l:ret = %d" % merlindent.vim_indentline())
  return l:ret
endfunction
