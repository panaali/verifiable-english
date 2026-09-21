-- All current manuscript tables fit on one page. Keep rows together in PDF.
-- Reconsider this filter if future results add a table taller than one page.
function Table(tbl)
  if FORMAT:match('latex') then
    return {
      pandoc.RawBlock('latex', '\\nopagebreak[4]\\begin{minipage}{\\linewidth}'),
      tbl,
      pandoc.RawBlock('latex', '\\end{minipage}\\par\\medskip')
    }
  end
end
