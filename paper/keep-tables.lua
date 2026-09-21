-- Paginate appendix tables and allow long identifier/path fragments to wrap.
-- Only add invisible TeX break opportunities; copied identifiers remain intact.
function Table(tbl)
  if not FORMAT:match('latex') then return tbl end
  return tbl:walk({Str = function(s)
    if #s.text < 13 then return nil end
    local result = pandoc.List()
    local pos = 1
    for ending in s.text:gmatch('()[/_:=#]') do
      result:insert(pandoc.Str(s.text:sub(pos, ending)))
      result:insert(pandoc.RawInline('latex', '\\allowbreak{}'))
      pos = ending + 1
    end
    if pos == 1 then return nil end
    if pos <= #s.text then result:insert(pandoc.Str(s.text:sub(pos))) end
    return result
  end})
end
