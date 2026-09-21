-- Use generated SVGs in the standalone HTML; PDF uses the same figures as PDF.
function Image(image)
  if FORMAT:match('html') then
    image.src = image.src:gsub('%.pdf$', '.svg')
  end
  return image
end
